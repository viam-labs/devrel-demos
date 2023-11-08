# Light up bot

See the tutorial for this project [here](https://docs.viam.com/tutorials/projects/light-up/).

This script configures an object detection robot using Viam.
Required hardware:
- A computer with a webcam (we are using a Mac)
- A Kasa Smart Plug
- A desk lamp

This robot will be able to turn the lights on/off when it detects a person in front of it.

As you get and set up the vision service params, you have to change the `model_path` to where your tflite package lives, and the `label_path` to where your text file lives. Note that the environment variables ROBOT_API_KEY, ROBOT_API_KEY_ID, and ROBOT_ADDRESS are also expected to be set.

This project requires that the smart plug to be attached to the light source (desk lamp in this case), and that a camera is configured as follows in the Viam app:

``` json
{
  "components": [
     {
      "depends_on": [],
      "model": "webcam",
      "name": "my-camera",
      "type": "camera",
      "attributes": {},
        "path": "change-this-with-your-own-camera-path"
      }
  ]
}
```
