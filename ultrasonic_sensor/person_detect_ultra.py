import asyncio
import os
import time

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.sensor import Sensor
from viam.components.base import Base
from viam.services.vision import VisionServiceClient

robot_secret = os.getenv('ROBOT_SECRET') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''
base_name = os.getenv('ROBOT_BASE') or 'viam_base'
camera_name = os.getenv('ROBOT_CAMERA') or 'face-cam'
pause_interval = os.getenv('PAUSE_INTERVAL') or 5

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

async def obstacle_detect(sensor, base):
    reading = (await sensor.get_readings())["distance"]
    print(reading)
    return reading

async def obstacle_detect_loop(sensor, base):
    while(True):
        reading = await obstacle_detect(sensor, base)
        if reading < 0.4:
            # stop the base if moving straight
            if base_state == "straight":
                await base.stop()
        await asyncio.sleep(.01)

async def person_detect(detector, sensor, base):
    while(True):
        # look for person
        found = False
        global base_state
        detections = await detector.get_detections_from_camera(camera_name)
        for d in detections:
            if d.confidence > .7:
                print(d.class_name)
                if (d.class_name == "person"):
                    found = True
        if (found):
            print("I see a person")
            # first manually call obstacle_detect - don't even start moving if someone in the way
            distance = await obstacle_detect(sensor, base)
            if (distance > .4):
                print("will move straight")
                base_state = "straight"
                await base.move_straight(distance=400, velocity=100)
                base_state = "stopped"
        else:
            "I will turn and look for a person"
            base_state = "spinning"
            await base.spin(90, 90)
            base_state = "stopped"

        await asyncio.sleep(pause_interval)

async def main():
    robot = await connect()
    base = Base.from_robot(robot, base_name)
    sensor = Sensor.from_robot(robot, "ultrasonic")
    detector = VisionServiceClient.from_robot(robot, "vis-stuff-detector")

    loop = asyncio.get_event_loop()

    # create a background task that looks for obstacles and stops the base if its moving
    obstacle_task = asyncio.create_task(obstacle_detect_loop(sensor, base))
    # create a background task that looks for a person and moves towards them, or turns and keeps looking
    person_task = asyncio.create_task(person_detect(detector, sensor, base))
    results= await asyncio.gather(obstacle_task, person_task, return_exceptions=True)
    print(results)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
