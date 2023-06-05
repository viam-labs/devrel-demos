import asyncio
import os
import time

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.sensor import Sensor
from viam.components.base import Base
from viam.services.vision import VisionClient

robot_secret = os.getenv('ROBOT_SECRET') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''
base_name = os.getenv('ROBOT_BASE') or 'tipsy-base'
camera_name = os.getenv('ROBOT_CAMERA') or 'cam'
#how to make this multiple sensors
#sensor_name = os.getenv('ROBOT_SENSOR') or 'ultrasonic'
pause_interval = os.getenv('PAUSE_INTERVAL') or 3

base_state = "stopped"

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=robot_secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(robot_address, opts)

async def obstacle_detect(sensor):
    reading = (await sensor.get_readings())["distance"]
    #print(reading)
    return reading 

async def obstacle_detect_loop(sensor, sensor2, sensor3, sensor4, sensor5, base):
    while(True):
        reading = await obstacle_detect(sensor)
        reading2 = await obstacle_detect(sensor2)
        reading3 = await obstacle_detect(sensor3)
        reading4 = await obstacle_detect(sensor4)
        reading5 = await obstacle_detect(sensor5)
        if reading < 0.4 or reading2 <0.4 or reading3 <0.4 or reading4 <0.4 or reading5 <0.4:
            # stop the base if moving straight
            if base_state == "straight":
                await base.stop()
                print("obstacle in front")
        await asyncio.sleep(.01)

async def person_detect(detector, sensor, sensor2, sensor3, sensor4, sensor5, base):
    while(True):
        # look for person
        found = False
        global base_state
        print("will detect")
        detections = await detector.get_detections_from_camera(camera_name)
        for d in detections:
            if d.confidence > .7:
                print(d.class_name)
                if (d.class_name == "Person"):
                    found = True
        if (found):
            print("I see a person")
            # first manually call obstacle_detect - don't even start moving if someone in the way
            distance = await obstacle_detect(sensor)
            distance2 = await obstacle_detect(sensor2)
            distance3 = await obstacle_detect(sensor3)
            distance4 = await obstacle_detect(sensor4)
            distance5 = await obstacle_detect(sensor5)
            if (distance > .4 or distance2 > .4 or distance3 > .4 or distance4 > .4 or distance5 > .4):
                print("will move straight")
                base_state = "straight"
                await base.move_straight(distance=800, velocity=250)
                base_state = "stopped"
        else:
            print("I will turn and look for a person")
            base_state = "spinning"
            await base.spin(45, 45)
            base_state = "stopped"

        await asyncio.sleep(pause_interval)

async def main():
    robot = await connect()
    base = Base.from_robot(robot, base_name)
    sensor = Sensor.from_robot(robot, "ultrasonic")
    sensor2= Sensor.from_robot(robot, "ultrasonic2")
    sensor3= Sensor.from_robot(robot, "ultrasonic3")
    sensor4= Sensor.from_robot(robot, "ultrasonic4")
    sensor5= Sensor.from_robot(robot, "ultrasonic5")
    detector = VisionClient.from_robot(robot, "myPeopleDetector")

    # create a background task that looks for obstacles and stops the base if its moving
    obstacle_task = asyncio.create_task(obstacle_detect_loop(sensor, sensor2, sensor3, sensor4, sensor5, base))
    # create a background task that looks for a person and moves towards them, or turns and keeps looking
    person_task = asyncio.create_task(person_detect(detector, sensor, sensor2, sensor3, sensor4, sensor5, base))
    results= await asyncio.gather(obstacle_task, person_task, return_exceptions=True)
    print(results)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())