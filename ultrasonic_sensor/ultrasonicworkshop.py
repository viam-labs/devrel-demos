import asyncio
import os
import time

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.sensor import Sensor
from viam.components.base import Base
from viam.proto.common import Vector3

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

async def main():
    robot = await connect()
    #initilazing rover base, the name between '' has to match the config component name
    base = Base.from_robot(robot, 'viam_base')

    #initilazing ultrasonic sensor, the name between '' has to match the config component name
    sensor = Sensor.from_robot(robot, "ultrasonic")

    for i in range(1000): 
        lst = []
        for i in range(10):
            readings = (await sensor.get_readings())["distance"]
            lst.append(readings)
        average_reading= sum(lst)/10
        print(average_reading)
        #300 mm is around a foot, so 0.3ish
        if average_reading < 0.4:
            # stop the base
            await base.stop()
            #moves the Viam Rover backward 500mm at 500mm/s
            await base.move_straight(distance=-500, velocity=500)
            print("avoid, move backwards")
            #turns the Viam Rover sideways with 90 degree angle
            await base.spin(velocity=100, angle=90)
            print("spin 90 degrees")
        else:
            #otherwise keep moving
            is_moving = await base.is_moving()
            if not is_moving:
                await base.set_power(linear=Vector3(x=0, y=100, z=0), angular=Vector3(x=0, y=0, z=0))
            print("not close to anything, move straight")
  
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
