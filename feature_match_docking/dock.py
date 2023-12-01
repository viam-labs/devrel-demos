import asyncio
import os
import time
import random

from viam import logging
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from action_python import Action


# these must be set, you can get them from your robot's 'CODE SAMPLE' tab
robot_api_key = os.getenv('ROBOT_API_KEY') or ''
robot_api_key_id = os.getenv('ROBOT_API_KEY_ID') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''

class robot_resources:
    robot = None
    dock_action = None

async def connect():
    opts = RobotClient.Options.with_api_key(api_key=robot_api_key, api_key_id=robot_api_key_id)
    return await RobotClient.at_address(robot_address, opts)

async def main():
    robot_resources.robot = await connect()

    robot_resources.dock_action = Action.from_robot(robot_resources.robot, name="dock-action")

    print(await robot_resources.dock_action.start())
    time.sleep(.2)
    print(await robot_resources.dock_action.is_running())
    print(await robot_resources.dock_action.status())

    await robot_resources.robot.close()


if __name__ == "__main__":
    asyncio.run(main())