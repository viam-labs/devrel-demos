# Pac-bot

This script is derived from the [Tipsy tutorial](https://docs.viam.com/tutorials/projects/tipsy/) but uses a custom "ghost" detector and an [*audioout* modular resource](https://github.com/viam-labs/audioout) for playing sound files.

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

* Upload the ghost-detector.tflite model and the labels.txt file, and set it up as an mlmodel and vision detector
* Set environment variables (see note below)
* run `pip3 install -r requirements.txt` in this directory
* run `python pacbot.py`

Note that the environment variables ROBOT_API_KEY, ROBOT_API_KEY_ID, and ROBOT_ADDRESS are expected to be set, and there are other environment variables you may want to set - see script.
