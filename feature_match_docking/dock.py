import asyncio
import os
import time
import random

from viam import logging
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.base import Base
from viam.components.camera import Camera
from viam.services.vision import VisionClient

# these must be set, you can get them from your robot's 'CODE SAMPLE' tab
robot_secret = os.getenv('ROBOT_SECRET') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''
velocity = 35
precise_spin = 2
big_spin = 6
normal_sleep = .1

class robot_resources:
    robot = None
    dock_detector = None
    base = None
    camera = None

async def connect():
    creds = Credentials(type="robot-location-secret", payload=robot_secret)
    opts = RobotClient.Options(refresh_interval=0, dial_options=DialOptions(credentials=creds), log_level=logging.DEBUG)
    return await RobotClient.at_address(robot_address, opts)

async def main():
    robot_resources.robot = await connect()

    robot_resources.dock_detector = VisionClient.from_robot(robot_resources.robot, name="match-chargepoint")
    robot_resources.base = Base.from_robot(robot=robot_resources.robot, name="viam_base")
    robot_resources.camera = Camera.from_robot(robot=robot_resources.robot, name="cam")

    docked = False
    sleep = normal_sleep
    detection_tries = 0

    while not docked:
        print("Looking for dock")

        img = await robot_resources.camera.get_image()
        detections = await robot_resources.dock_detector.get_detections(img)

        if len(detections) == 1:
            print(detections)
            relative_size = (detections[0].x_max - detections[0].x_min)/img.width
            centered = (detections[0].x_min + ((detections[0].x_max - detections[0].x_min)/2)) /img.width - .5
            print(centered, relative_size)
    
            # try to get it more centered
            if abs(centered) > .04:
                if centered > 0:
                    await robot_resources.base.spin(precise_spin, -velocity)
                else:
                    await robot_resources.base.spin(precise_spin,velocity)
            else:
               await robot_resources.base.move_straight(10,velocity)
            if relative_size > .55:
                docked = True
            sleep = .5
        else:
            detection_tries = detection_tries + 1
            if detection_tries == 3:
                await robot_resources.base.spin(big_spin, velocity)
                sleep = normal_sleep
                detection_tries = 0
        time.sleep(sleep)
    

    await robot_resources.robot.close()


if __name__ == "__main__":
    asyncio.run(main())