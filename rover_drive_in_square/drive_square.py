import asyncio
import os

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.base import Base

# These must be set, you can get them from your robot's 'CODE SAMPLE' tab
robot_api_key = os.getenv('ROBOT_API_KEY') or ''
robot_api_key_id = os.getenv('ROBOT_API_KEY_ID') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''


async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key=robot_api_key,
      api_key_id=robot_api_key_id
    )
    return await RobotClient.at_address(robot_address, opts)

async def moveInSquare(base):
    for _ in range(4):
        # moves the Viam Rover forward 500mm at 500mm/s
        await base.move_straight(velocity=500, distance=500)
        print("move straight")
        # spins the Viam Rover 90 degrees at 100 degrees per second
        await base.spin(velocity=100, angle=90)
        print("spin 90 degrees")

async def main():
    robot = await connect()
    roverBase = Base.from_robot(robot, 'viam_base')

    print('Resources:')
    print(robot.resource_names)

    await moveInSquare(roverBase)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())

