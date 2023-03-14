import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.camera import Camera
from viam.components.types import CameraMimeType
from viam.services.vision import VisionServiceClient, VisModelConfig, VisModelType, Detection
from PIL import ImageDraw
from kasa import Discover, SmartPlug

ROBOT_URL = 'PUT YOUR URL HERE!!!'
ROBOT_SECRET = 'PUT YOUR SECRET HERE!!!'

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=ROBOT_SECRET)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(ROBOT_URL, opts)

def drawBox(d, frame):
  rect = [d.x_min, d.y_min, d.x_max, d.y_max]
  img1 = ImageDraw.Draw(frame)
  img1.rectangle(rect, outline="red")
  return frame

async def main():
    robot = await connect()

    print('Resources:')
    print(robot.resource_names)

    camera = Camera.from_robot(robot, "camera")
    image = await camera.get_image()

    # Get and setup vision service
    vision = VisionServiceClient.from_robot(robot)
    params = {"model_path": "/Users/hazalmestci/Downloads/effdet0.tflite", "label_path": "/Users/hazalmestci/Downloads/labels.txt", "num_threads": 1}
    personDet = VisModelConfig(name="person_detector", type=VisModelType("tflite_detector"), parameters=params)
    await vision.add_detector(personDet)
    names = await vision.get_detector_names()
    print(names)

    N = 100
      
    #example: plug = SmartPlug('10.1.11.221')
    plug = SmartPlug('replace with the host of your plug')
    await plug.update()

    await plug.turn_off()
    state = "off"
    for i in range(N):
        image = await camera.get_image()
        detections = await vision.get_detections(image, "person_detector")
        found = False
        for d in detections:
            if d.confidence > 0.8:
                print(d)
                print()
                # image = drawBox(d, image)
                # image.show()
                if d.class_name.lower() == "person":
                    print("This is a person!")
                    found = True
             
        if found:
            # Put the code here to turn on the smart plug
            await plug.turn_on()
            await plug.update()
            print("turning on")
            state = "on"
        else:
            print("There's nobody here")
            # Put the code here to turn off the smart plug
            await plug.turn_off()
            await plug.update()
            print("turning off")
            state = "off"

    await asyncio.sleep(5)
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
