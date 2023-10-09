import asyncio
import os
import io
import random
import time
import datetime
import re

from PIL import Image
from viam import logging
from viam.robot.client import RobotClient
from viam.app.viam_client import ViamClient
from speech import SpeechService
from viam.rpc.dial import Credentials, DialOptions
from viam.components.camera import Camera
from viam.components.servo import Servo
from viam.services.vision import VisionClient

# these must be set, you can get them from your robot's 'CODE SAMPLE' tab
robot_secret = os.getenv('ROBOT_SECRET') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''
robot_part_id = os.getenv('ROBOT_PART') or ''

# if set to false, will just repeat the wording passed in
use_completion = True
# use servos for "head" tracking and claw movement
use_servos = True

fact_list = [
    "favorite color",
    "favorite musician",
    "favorite science fiction robot",
    "favorite season",
    "favorite food"
]

class robot_resources:
    speech =  None
    fd = None
    fc = None
    camera = None
    head = None
    claw = None

async def robot_connect():
    creds = Credentials(type="robot-location-secret", payload=robot_secret)
    opts = RobotClient.Options(refresh_interval=0, dial_options=DialOptions(credentials=creds), log_level=logging.DEBUG)
    return await RobotClient.at_address(robot_address, opts)


async def viam_connect() -> ViamClient:
    dial_options = DialOptions(
        auth_entity=robot_address,  # The URL of your robot.
        credentials=Credentials(
            type='robot-location-secret',
            payload=robot_secret
        )
    )
    return await ViamClient.create_from_dial_options(dial_options)

async def detect_face():
    frame = await robot_resources.camera.get_image()   
    detections = await robot_resources.fd.get_detections(frame)
    if len(detections) == 1:
        # for now only look for a single face, as it might be hard to manage multiple
        detection = detections[0]
        if detection.confidence > .75:
            im = frame
            cropped = im.crop((detection.x_min, detection.y_min, detection.x_max, detection.y_max))
            #cropped.show()
            await track_face(im, detection)
            return cropped
    return None

async def track_face(im, detection):
    if not use_servos:
        return
    # position 0-1, where .5 is in the center of vision
    face_pos = ((detection.x_max-detection.x_min)/2 + detection.x_min)/im.size[0]
    # how many degrees (positive or negative) to move out of a max move size of 25
    move_degs = (1 - face_pos * 2) * 25
    new_position = int(await robot_resources.head.get_position() + move_degs)
    if new_position > 180:
        new_position = 180
    elif new_position < 0:
        new_position = 0
    await robot_resources.head.move(new_position)

async def face_fact(photo):
    c = await robot_resources.fc.get_classifications(photo, 1)
    print(c)
    if len(c) > 0 and c[0].confidence > .9:
        print(c)
        c_spl = c[0].class_name.split('_')
        secs_ago = int(datetime.datetime.timestamp(datetime.datetime.now())) - int(c_spl[0])
        when = ""
        if (secs_ago - (60 * 60 * 18)) > 0:
            days_ago = secs_ago / 86400
            if days_ago > 1.5:
                when = "a couple days ago"
            else:
                when = "yesterday"
        else:
            when = "just today"
        return { "when": when, "fact_type": c_spl[1].replace('-', ' '), "fact_value": c_spl[2].replace('-', ' ') }


async def say(text):
    if use_completion:
        said = await robot_resources.speech.completion("write a completion to ask '" + text + "'")
    else:
        said = await robot_resources.speech.say(text)
    return said

async def push_face_image(images):
    face_photo = await detect_face()
    if face_photo != None:
        buf = io.BytesIO()
        face_photo.save(buf, format='JPEG')
        images.append(buf.getvalue())
    return images

async def collect_fact_and_images():
    resp = {"images": [], "fact_type": None, "fact_response": None}

    resp["images"] = await push_face_image(resp["images"])

    fact_type = random.choice(fact_list)
    resp["fact_type"] = fact_type

    # clear leftover commands
    commands = await robot_resources.speech.get_commands(10)
    print(commands)
    said = await say("hi, I don't think we have met, what is your " + fact_type + "'")
    resp["images"] = await push_face_image(resp["images"])
    time.sleep(2)
    print("will listen")
    await robot_resources.speech.listen_trigger('command')
    command = None
    command_check = 0
    resp["images"] = await push_face_image(resp["images"])
    while command == None:
        resp["images"] = await push_face_image(resp["images"])
        commands = await robot_resources.speech.get_commands(2)
        if len(commands) > 0:
            print(commands)
            # try to avoid recording the robot speaking
            if (commands[0] == said) or (len(said) > 20 and re.search(commands[0], said)):
                if len(commands) > 1:
                    command = command[1]
            else:
                command = commands[0]
                await say("I like " + command + " too. Great talking to you, goodbye.")
                for x in range(0, 10):
                    resp["images"] = await push_face_image(resp["images"])
                resp["fact_response"] = command
        time.sleep(.2)
        resp["images"] = await push_face_image(resp["images"])

        command_check = command_check + 1
        if command_check == 20:
            resp["images"] = await push_face_image(resp["images"])
            said = await say("Sorry, I didn't hear you - what is your " + fact_type + "'")
        elif command_check == 40:
            await say("Sorry, I still did not year you, but nice to meet you")
            break
    
    return resp

async def move_claw(angle, wait):
    if not use_servos:
        return
    await robot_resources.claw.move(angle)
    time.sleep(wait)
    await robot_resources.claw.move(0)
    time.sleep(wait)
    await robot_resources.claw.move(angle)
    time.sleep(wait)
    await robot_resources.claw.move(0)
    time.sleep(.5)

async def send_images(resp):
    print("got " + str(len(resp["images"])) + " images")
    print(resp["fact_response"])
    if resp["fact_response"] != None and len(resp["images"]) >= 10:
        now = str(int(datetime.datetime.timestamp(datetime.datetime.now())))
        for i in resp["images"]:
            tags = []
            tag = re.sub(r'\W+', '-', (now + "_" + resp["fact_type"] + "_" + resp["fact_response"]))
            tags.append(tag)
            filename = tag + ".jpg"
            await robot_resources.app_client.data_client.file_upload(part_id=robot_part_id, component_name="face-detector", 
                                file_name=filename, file_extension=".jpg", data=i, tags=tags)

async def main():
    robot = await robot_connect()
    robot_resources.app_client = await viam_connect()

    print('Resources:')
    print(robot.resource_names)
    robot_resources.speech = SpeechService.from_robot(robot, name="speechio")
    robot_resources.fd = VisionClient.from_robot(robot, name="face-detector")
    robot_resources.fc= VisionClient.from_robot(robot, "fact-classifier")
    robot_resources.camera = Camera.from_robot(robot=robot, name="cam")

    if use_servos:
        robot_resources.head = Servo.from_robot(robot=robot, name="head-servo")
        robot_resources.claw = Servo.from_robot(robot=robot, name="claw")

    while True:
        face_photo = await detect_face()
        if face_photo != None:
            print("I see a face")
            fact = await face_fact(face_photo)
            if fact == None:
                # interact and collect images to retrain model
                asyncio.ensure_future(move_claw(10, 1))
                resp = await collect_fact_and_images()
                await send_images(resp)
            else:
                # interact regarding previous encounter and learnings
                asyncio.ensure_future(move_claw(25, .2))
                await say("Hello again, we met " + fact["when"] + ".  I remember your " + fact["fact_type"] + " is " + fact["fact_value"])
                still_here = True
                while still_here:
                    time.sleep(1)
                    await robot_resources.speech.listen_trigger("completion")
                    time.sleep(12)
                    face_photo = await detect_face()
                    if face_photo != None:
                        still_here = True
                    else:
                        still_here = False
    # Don't forget to close the robot when you're done!
    await robot.close()
    await app_client.close()

if __name__ == '__main__':
    # a hack to just keep re-spawning on any errors encountered (like disconnect from robot)
    try:
        asyncio.run(main())
    except:
        asyncio.run(main())

