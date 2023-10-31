# Creepsy! 
A scary drink server robot using the Viam platform. This script is derived from the [Tipsy tutorial](https://docs.viam.com/tutorials/projects/tipsy/) but uses an [*audioout* modular resource](https://github.com/viam-labs/audioout) to play scary sound files.

To run this:
* Set up the audioout module and configure a service named 'audioout':

``` json
    {
      "attributes": {},
      "name": "audioout",
      "type": "audioout",
      "namespace": "viam-labs",
      "model": "viam-labs:audioout:pygame"
    }
```
* Install the prerequisites to your Raspberry Pi:

``` bash
sudo apt update && sudo apt upgrade -y
sudo apt-get install python3
sudo apt install python3-pip python3-venv
sudo apt install python3-pyaudio
sudo apt-get install alsa-tools alsa-utils
sudo apt-get install flac
```

* Upload the effdet0.tflite model and the labels.txt file, and set it up as an mlmodel and vision detector
* Set environment variables (see note below)
* run `pip3 install -r requirements.txt` in this directory
* run `python creepsy.py`

**Required environment variables:**

[Learn about authenticating with the Viam SDK](https://docs.viam.com/program/run/#authentication).

- `ROBOT_SECRET`
- `ROBOT_ADDRESS`

You can obtain the robot’s secret and address from the app’s Code sample tab, which is both needed to send API calls to the robot from the [Viam SDKs](https://docs.viam.com/program/apis/).

**Optional environment variables:**

- `ROBOT_BASE` (name of the `base` component in the robot configuration, defaults to `creepsy-base`)
- `ROBOT_CAMERA` (name of the `camera` component in the robot configuration, defaults to `cam`)
- `ROBOT_SENSORS` (names of the ultrasonic `sensor` components in the robot configuration as a comma-separated list, defaults to `ultrasonic,ultrasonic2`)
- `DETECTOR_NAME` (name of the `detector` in the robot configuration, defaults to `people-detector`)
- `PAUSE_INTERVAL` (number of seconds to wait between searching for people to serve, defaults to 3)
- `CHASE_LABEL`(label of the object you are following, defaults to person)
