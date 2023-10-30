import asyncio
import os

from audioout import Audioout
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.sensor import Sensor
from viam.components.base import Base
from viam.services.vision import VisionClient

robot_secret = os.getenv('ROBOT_SECRET') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''
#change this if you named your base differently in your robot configuration
base_name = os.getenv('ROBOT_BASE') or 'creepsy-base'
#change this if you named your camera differently in your robot configuration
camera_name = os.getenv('ROBOT_CAMERA') or 'cam'
# change this if you named your sensors differently in your robor configuration
sensor_names = (os.getenv("ROBOT_SENSORS") or "ultrasonic,ultrasonic2").split(",")
pause_interval = os.getenv('PAUSE_INTERVAL') or 3
detector_name = os.getenv('DETECTOR_NAME') or 'people-detector'
chase_label = os.getenv('CHASE_LABEL') or 'person'

if isinstance(pause_interval, str):
    pause_interval = int(pause_interval)

base_state = "stopped"

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=robot_secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(robot_address, opts)

async def play_sound(ao, filename, loop_count, block):
    print("starting play sound " + filename)
    await ao.play("sounds/" + filename, loop_count, 0, 0, block)
    print("done play sound " + filename)

async def stop_sound(ao):
    print("stopping sound")
    await ao.stop()
    print("done stopping sound")

async def obstacle_detect(sensor: Sensor):
    reading = (await sensor.get_readings())["distance"]
    return reading 

async def gather_obstacle_readings(sensors: list[Sensor]):
    return await asyncio.gather(*[obstacle_detect(sensor) for sensor in sensors])

async def obstacle_detect_loop(sensors: list[Sensor], base: Base):
    while True:
        distances = await gather_obstacle_readings(sensors)
        if any(distance < 0.4 for distance in distances):
            # stop the base if moving straight
            if base_state == "straight":
                await base.stop()
                print("obstacle in front")
        await asyncio.sleep(0.01)

async def person_detect(detector: VisionClient, sensors: list[Sensor], base: Base, ao):
    while True:
        action = ""
        global base_state
        # look for a person
        print("will detect")
        detections = await detector.get_detections_from_camera(camera_name,timeout=10)
        print("got detections")
        for d in detections:
            if d.confidence > .7:
                print(d.class_name)
                if (d.class_name == "Person"):
                    action = "chase"
        
        if (action == "chase"):
            await stop_sound(ao)
            await play_sound(ao, 'creepy-horror-sound-possessed-2-laughter-vol-001-167400.mp3', 10, False)
            print("I have to chase the person")
            # first manually call obstacle_detect - don't even start moving if something is in the way
            distances = await gather_obstacle_readings(sensors)
            if all(distance > 0.4 for distance in distances):
                print("will move straight")
                base_state = "straight"
                await base.move_straight(distance=800, velocity=250)
                base_state = "stopped"
        else:
            await stop_sound(ao)
            await play_sound(ao, 'spooky-halloween-effects-with-thunder-121665.mp3', 0, False)
            print("I will turn and look for a person")
            base_state = "spinning"
            await base.spin(45, 45)
            base_state = "stopped"

        print("I will sleep")
        await asyncio.sleep(pause_interval)

async def main():
    robot = await connect()
    base = Base.from_robot(robot, base_name)
    sensors = [Sensor.from_robot(robot, sensor_name) for sensor_name in sensor_names]
    detector = VisionClient.from_robot(robot, detector_name)
    ao = Audioout.from_robot(robot, name="audioout")

    await stop_sound(ao)
    await play_sound(ao, 'Free - Scream 7.mp3', 0, True)

    # create a background task that looks for obstacles and stops the base if its moving
    obstacle_task = asyncio.create_task(obstacle_detect_loop(sensors, base))
    # create a background task that looks for a person and moves towards them, or turns and keeps looking
    person_task = asyncio.create_task(person_detect(detector, sensors, base, ao))
    results= await asyncio.gather(obstacle_task, person_task, return_exceptions=True)
    print(results)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
