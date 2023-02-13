import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.base import Base

robot_secret = ''
robot_address = ''

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=robot_secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
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

