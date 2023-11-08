import asyncio
import os
import time
import threading

from audioout import Audioout
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.sensor import Sensor
from viam.components.base import Base
from viam.services.vision import VisionClient

# These must be set, you can get them from your robot's 'CODE SAMPLE' tab
robot_api_key = os.getenv('ROBOT_API_KEY') or ''
robot_api_key_id = os.getenv('ROBOT_API_KEY_ID') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''
#change this if you named your base differently in your robot configuration
base_name = os.getenv('ROBOT_BASE') or 'tipsy-base'
#change this if you named your camera differently in your robot configuration
camera_name = os.getenv('ROBOT_CAMERA') or 'cam'
pause_interval = os.getenv('PAUSE_INTERVAL') or .1
detector_name = os.getenv('DETECTOR_NAME') or 'ghostDetector'
run_label = os.getenv('RUN_LABEL') or 'purple_ghost'
chase_label = os.getenv('CHASE_LABEL') or 'cyan_ghost'

base_state = "stopped"

async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key=robot_api_key,
      api_key_id=robot_api_key_id
    )
    return await RobotClient.at_address(robot_address, opts)

async def play_sound(ao, filename, loop_count, block):
    print("starting play sound " + filename)
    await ao.play("sounds/" + filename, loop_count, 0, 0, block)
    print("done play sound " + filename)

async def stop_sound(ao):
    print("stopping sound")
    await ao.stop()
    print("done stopping sound")

async def obstacle_detect(sensor):
    reading = (await sensor.get_readings())["distance"]
    return reading 

async def obstacle_detect_loop(sensor, base):
    while(True):
        reading = await obstacle_detect(sensor)
        if reading < 0.4:
            # stop the base if moving straight
            if base_state == "straight":
                await base.stop()
                print("obstacle in front")
        await asyncio.sleep(.01)

async def ghost_detect(detector, sensor, base, ao):
    while(True):
        action = ""
        global base_state
        print("will detect")
        detections = await detector.get_detections_from_camera(camera_name=camera_name,timeout=10)
        print("got detections")
        for d in detections:
            if d.confidence > .7:
                print(d.class_name)
                if (d.class_name == run_label):
                    action = "run"
                elif (d.class_name == chase_label):
                    action = "chase"
        
        if (action == "run"):
            await stop_sound(ao)
            await play_sound(ao, 'siren_1.wav', 10, False)

            print("I need to run from the ghost")
            # first manually call obstacle_detect - don't even start moving if something is in the way
            distance = await obstacle_detect(sensor)
            if (distance > .4):
                base_state = "spinning"
                await base.spin(180, 90)
                base_state = "straight"
                await base.move_straight(distance=800, velocity=250)
                base_state = "stopped"
        elif (action == "chase"):
            await stop_sound(ao)
            await play_sound(ao, 'power_pellet.wav', 0, True)
            await play_sound(ao, 'retreating.wav', 0, False)
            print("I need chase the ghost")
            # first manually call obstacle_detect - don't even start moving if something is in the way
            distance = await obstacle_detect(sensor)
            if (distance > .4 or distance2 > .4):
                base_state = "straight"
                await base.move_straight(distance=800, velocity=350)
                base_state = "stopped"
        else:
            await stop_sound(ao)
            await play_sound(ao, 'pacman_chomp.wav', 0, False)
            print("I will turn then go straight")
            base_state = "spinning"
            await base.spin(45, 90)
            base_state = "straight"
            await base.move_straight(distance=400, velocity=250)
            base_state = "stopped"

        print("Will sleep")
        await asyncio.sleep(pause_interval)

async def main():
    robot = await connect()
    base = Base.from_robot(robot, base_name)
    sensor = Sensor.from_robot(robot, "ultrasonic")
    detector = VisionClient.from_robot(robot, detector_name)
    ao = Audioout.from_robot(robot, name="audioout")

    await stop_sound(ao)
    await play_sound(ao, 'game_start.wav', 0, True)

    # create a background task that looks for obstacles and stops the base if its moving
    obstacle_task = asyncio.create_task(obstacle_detect_loop(sensor, base))
    # create a background task that looks for a ghost runs from a purple one, chases a cyan one, or turns and goes straight
    ghost_task = asyncio.create_task(ghost_detect(detector, sensor, base, ao))

    results= await asyncio.gather(obstacle_task, ghost_task, return_exceptions=True)
    print(results)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())