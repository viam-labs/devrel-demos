import asyncio
import os

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.vision import VisionClient, VisModelConfig, VisModelType, Detection
from kasa import Discover, SmartPlug

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

    detector = VisionClient.from_robot(robot, "myPeopleDetector")

    N = 100
      
    #example: plug = SmartPlug('10.1.11.221')
    plug = SmartPlug('replace with the host IP of your plug')
    await plug.update()
    await plug.turn_off()
    state = "off"
    for i in range(N):
        #make sure that your camera name in the app matches "my-camera"       
        detections = await detector.get_detections_from_camera("my-camera")
        found = False
        for d in detections:
            if d.confidence > 0.8:
                print(d.class_name)
                if d.class_name.lower() == "person":
                    print("This is a person!")
                    found = True
        if found:
            #turn on the smart plug
            await plug.turn_on()
            await plug.update()
            print("turning on")
            state = "on"
        else:
            print("there's nobody here")
            #turn off the smart plug
            await plug.turn_off()
            await plug.update()
            print("turning off")
            state = "off"

    await asyncio.sleep(5)
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
