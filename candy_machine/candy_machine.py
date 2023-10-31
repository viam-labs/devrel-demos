import asyncio
import os
import time

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.motor import Motor
from viam.components.board import Board

# these must be set, you can get them from your robot's 'CODE SAMPLE' tab
robot_api_key = os.getenv('ROBOT_API_KEY') or ''
robot_api_key_id = os.getenv('ROBOT_API_KEY_ID') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''


async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key=robot_api_key,
      api_key_id=robot_api_key_id
    )
    return await RobotClient.at_address(robot_address, opts)


async def main():
    robot = await connect()

    # update these based on how you named your stepper, board, and how you wired your sensor
    stepper = Motor.from_robot(robot, 'stepper')
    board = Board.from_robot(robot, 'pi')
    sensor_pin = await board.gpio_pin_by_name('37')

    move_count = 0
    while True:
        pin_status = await sensor_pin.get()
        # pin status is False if it senses something close to it
        if pin_status == False:
            await stepper.go_for(rpm=80,revolutions=.1)
            move_count = move_count + 1
            if move_count % 10 == 0:
                # try to break any jams
                await stepper.go_for(rpm=150,revolutions=-.2) 
        time.sleep(.2)


    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())

