import asyncio
import os

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.camera import Camera
from viam.components.types import CameraMimeType
from viam.services.vision import VisionClient, VisModelConfig, VisModelType, Detection
from PIL import ImageDraw
from kasa import Discover, SmartPlug

# These must be set, you can get them from your robot's 'CODE SAMPLE' tab
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

    # This string should match your camera component name in your robot config on the Viam app
    camera = Camera.from_robot(robot, "my-camera")
    detector = VisionClient.from_robot(robot, "myPeopleDetector")

    N = 100
      
    #example: plug = SmartPlug('10.1.11.221')
    plug = SmartPlug('replace with the host IP of your plug')
    await plug.update()
    await plug.turn_off()
    state = "off"
    for i in range(N):
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
            print("There's nobody here")
            #turn off the smart plug
            await plug.turn_off()
            await plug.update()
            print("turning off")
            state = "off"

    await asyncio.sleep(5)
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
