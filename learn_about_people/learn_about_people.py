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
from viam.services.vision import VisionClient

# these must be set, you can get them from your robot's 'CODE SAMPLE' tab
robot_secret = os.getenv('ROBOT_SECRET') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''
robot_part_id = os.getenv('ROBOT_PART') or ''

# if set to false, will just repeat the wording passed in
use_completion = True
fact_list = [
    "favorite color",
    "favorite musician",
    "favorite science fiction robot",
    "favorite season",
    "favorite food"
]

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

async def detect_face(camera, detector):
    frame = await camera.get_image()   
    detections = await detector.get_detections(frame)
    if len(detections) == 1:
        # for now only look for a single face, as it might be hard to manage multiple
        detection = detections[0]
        if detection.confidence > .75:
            im = Image.open(io.BytesIO(frame.data))
            cropped = im.crop((detection.x_min, detection.y_min, detection.x_max, detection.y_max))
            #cropped.show()
            return cropped
    return None

async def face_fact(classifier, photo):
    c = await classifier.get_classifications(photo, 1)
    print(c)
    if len(c) > 0 and c[0].confidence > .5:
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


async def say(speech, text):
    if use_completion:
        said = await speech.completion("write a question asking '" + text + "'")
    else:
        said = await speech.say(text)
    return said

async def push_face_image(cam, fd, images):
    face_photo = await detect_face(cam, fd)
    if face_photo != None:
        buf = io.BytesIO()
        face_photo.save(buf, format='JPEG')
        images.append(buf.getvalue())
    return images

async def collect_fact_and_images(speech, cam, fd):
    resp = {"images": [], "fact_type": None, "fact_response": None}

    resp["images"] = await push_face_image(cam, fd, resp["images"])

    fact_type = random.choice(fact_list)
    resp["fact_type"] = fact_type

    # clear leftover commands
    commands = await speech.get_commands(10)
    print(commands)
    said = await say(speech, "hi, I don't think we have met, what is your " + fact_type + "'")
    resp["images"] = await push_face_image(cam, fd, resp["images"])
    time.sleep(2)
    print("will listen")
    await speech.listen_trigger('command')
    command = None
    command_check = 0
    resp["images"] = await push_face_image(cam, fd, resp["images"])
    while command == None:
        resp["images"] = await push_face_image(cam, fd, resp["images"])
        commands = await speech.get_commands(2)
        if len(commands) > 0:
            print(commands)
            if (commands[0] == said) or (len(said) > 20 and re.search(commands[0], said)):
                if len(commands) > 1:
                    command = command[1]
            else:
                command = commands[0]
                await say(speech, "I like " + command + " too. Great talking to you, goodbye.")
                for x in range(0, 10):
                    resp["images"] = await push_face_image(cam, fd, resp["images"])
                resp["fact_response"] = command
        time.sleep(.2)
        resp["images"] = await push_face_image(cam, fd, resp["images"])

        command_check = command_check + 1
        if command_check == 30:
            resp["images"] = await push_face_image(cam, fd, resp["images"])
            said = await say(speech, "Sorry, I didn't hear you - what is your " + fact_type + "'")
        elif command_check == 60:
            await say(speech, "Sorry, I still did not year you, but nice to meet you")
            break
    
    return resp

async def main():
    robot = await robot_connect()
    app_client = await viam_connect()

    print('Resources:')
    print(robot.resource_names)
    speech = SpeechService.from_robot(robot, name="speech")
    fd = VisionClient.from_robot(robot, name="face-detector")
    fc= VisionClient.from_robot(robot, "fact-classifier")
    cam = Camera.from_robot(robot=robot, name="cam")

    while True:
        # check if we have a fact for this face - try 10 times so as to have higher chance of detection
        fact = None
        for x in range(0, 10):
            face_photo = await detect_face(cam, fd)
            if face_photo != None:
                print("I see a face")
                f = await face_fact(fc, face_photo)
                if f != None:
                    fact = f
                    break
        if fact == None:
            resp = await collect_fact_and_images(speech, cam, fd)
            print("got " + str(len(resp["images"])) + " images")
            print(resp["fact_response"])
            if resp["fact_response"] != None and len(resp["images"]) >= 10:
                now = str(int(datetime.datetime.timestamp(datetime.datetime.now())))
                for i in resp["images"]:
                    tags = []
                    tag = re.sub(r'\W+', '-', (now + "_" + resp["fact_type"] + "_" + resp["fact_response"]))
                    tags.append(tag)
                    filename = tag + ".jpg"
                    await app_client.data_client.file_upload(part_id=robot_part_id, component_name="face-detector", 
                                        file_name=filename, file_extension=".jpg", data=i, tags=tags)
        else:
            await say(speech, "Hello again, we met " + fact["when"] + ".  I remember your " + fact["fact_type"] + " is " + fact["fact_value"])
            still_here = True
            last_when = fact["when"]
            while still_here:
                time.sleep(1)
                await speech.listen_trigger("completion")
                time.sleep(20)
                face_photo = await detect_face(cam, fd)
                if face_photo != None:
                    f = await face_fact(fc, face_photo)
                    if f == None or f["when"] != last_when:
                        still_here = False
                        await speech.say("Goodbye")
                else:
                    await speech.say("Goodbye")
    # Don't forget to close the robot when you're done!
    await robot.close()
    await app_client.close()

if __name__ == '__main__':
    asyncio.run(main())


