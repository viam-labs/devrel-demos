import asyncio

from viam.robot.client import RobotClient
from viam.components.board import Board
from viam.components.motor import Motor
from viam.rpc.dial import Credentials, DialOptions

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

    party=Board.from_robot(robot,"party")
    # Note that the pin supplied is a placeholder. Please change this to a valid pin you are using.
    party_return_value = await party.gpio_pin_by_name("37")
    print(f"party gpio_pin_by_name return value: {party_return_value.get()}")

    start = Motor.from_robot(robot,"start")
    start_return_value = await start.is_moving()
    print(f"start is_moving return value: {start_return_value}")

    while True: 

        print(party_return_value.get())
        while (await party_return_value.get()) == True:
            await start.set_power(.8)
            await asyncio.sleep(0.1)
            if (await party_return_value.get()) == False: 
                break
        await start.set_power(0)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())