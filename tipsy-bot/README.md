# Tipsy Bot

A drink server robot using Viam platform. [Learn how it's built!](https://docs.viam.com/tutorials/projects/tipsy/)

## Getting Started

0. Upload the `effdet0.tflite` model and the `labels.txt` file [in the app](https://app.viam.com/data/models), and set it up as an mlmodel and vision detector under the robot configuration
0. Set environment variables (see note below)
0. run `pip3 install -r requirements.txt` in this directory
0. run `python tipsy.py`

**Required environment variables:**

[Learn about authenticating with the Viam SDK](https://docs.viam.com/program/run/#authentication).

- `ROBOT_SECRET`
- `ROBOT_ADDRESS`
You can obtain the robot’s address and location secret from the app’s Code sample tab, which is both needed to send API calls to the robot from the [Viam SDKs](https://docs.viam.com/program/apis/).
**Optional environment variables:**

- `ROBOT_BASE` (name of the `base` component in the robot configuration, defaults to `tipsy-base`)
- `ROBOT_CAMERA` (name of the `camera` component in the robot configuration, defaults to `cam`)
- `ROBOT_SENSORS` (names of the ultrasonic `sensor` components in the robot configuration as a comma-separated list, defaults to `ultrasonic,ultrasonic2`)
- `PAUSE_INTERVAL` (number of seconds to wait between searching for people to serve, defaults to 3)
