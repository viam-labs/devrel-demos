import asyncio
import os

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.sensor import Sensor
from viam.components.base import Base
from viam.services.vision import VisionClient
from viam.services.sensors import SensorsClient

robot_secret = os.getenv("ROBOT_SECRET") or ""
robot_address = os.getenv("ROBOT_ADDRESS") or ""
# change this if you named your base differently in your robot configuration
base_name = os.getenv("ROBOT_BASE") or "tipsy-base"
# change this if you named your camera differently in your robot configuration
camera_name = os.getenv("ROBOT_CAMERA") or "cam"
# change this if you named your sensors differently in your robor configuration
pause_interval = os.getenv("PAUSE_INTERVAL") or 3

if isinstance(pause_interval, str):
    pause_interval = int(pause_interval)

base_state = "stopped"


async def connect():
    creds = Credentials(
        type="robot-location-secret",
        payload=robot_secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(robot_address, opts)


async def get_obstacle_readings(sensors: list[Sensor]):
    return await [r["distance"] for r in sensors_svc.get_readings(sensors)]


async def obstacle_detect_loop(sensors: list[Sensor], base: Base):
    while True:
        distances = await gather_obstacle_readings(sensors)
        if any(distance < 0.4 for distance in distances):
            # stop the base if moving straight
            if base_state == "straight":
                await base.stop()
                print("obstacle in front")
        await asyncio.sleep(0.01)


async def person_detect(detector: VisionClient, sensors: list[Sensor], base: Base):
    while True:
        # look for person
        found = False
        global base_state
        print("will detect")
        detections = await detector.get_detections_from_camera(camera_name)
        for d in detections:
            if d.confidence > 0.7:
                print(d.class_name)
                if d.class_name == "Person":
                    found = True
        if found:
            print("I see a person")
            # first manually call obstacle_detect - don't even start moving if someone is in the way
            distances = await get_obstacle_readings(sensors)
            if all(distance > 0.4 for distance in distances):
                print("will move straight")
                base_state = "straight"
                await base.move_straight(distance=800, velocity=250)
                base_state = "stopped"
        else:
            print("I will turn and look for a person")
            base_state = "spinning"
            await base.spin(45, 45)
            base_state = "stopped"

        await asyncio.sleep(pause_interval)


async def main():
    robot = await connect()
    base = Base.from_robot(robot, base_name)
    sensors_svc = SensorsClient.from_robot(robot=robot, name="builtin")
    sensors = await sensors_svc.get_sensors()
    detector = VisionClient.from_robot(robot, "myPeopleDetector")

    # create a background task that looks for obstacles and stops the base if its moving
    obstacle_task = asyncio.create_task(obstacle_detect_loop(sensors, base))
    # create a background task that looks for a person and moves towards them, or turns and keeps looking
    person_task = asyncio.create_task(person_detect(detector, sensors, base))
    results = await asyncio.gather(obstacle_task, person_task, return_exceptions=True)
    print(results)

    await robot.close()


if __name__ == "__main__":
    asyncio.run(main())
