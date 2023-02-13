import asyncio
import os
import time

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.motor import Motor
from viam.components.board import Board

robot_secret = os.getenv('ROBOT_SECRET') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=robot_secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(robot_address, opts)

async def main():
    robot = await connect()

    stepper = Motor.from_robot(robot, 'stepper')
    board = Board.from_robot(robot, 'pi')
    sensor_pin = await board.gpio_pin_by_name('37')

    while True:
        pin_status = await sensor_pin.get()
        if pin_status == False:
            await stepper.go_for(rpm=40,revolutions=.1)
        time.sleep(.2)


    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())

