# Light up bot

This script configures an object detection robot using Viam. 
Required hardware:
- A computer with a webcam (we are using a Mac)
- A Kasa Smart Plug
- A desk lamp

This robot will be able to turn the lights on/off when it detects a person in front of it.

As you get and set up the vision service params, you have to change the `model_path` to where your tflite package lives, and the `label_path` to where your text file lives. Note that the environment variables ROBOT_SECRET and ROBOT_ADDRESS are also expected to be set.

Project asks for the smart plug to be attached to the light source (desk lamp in this case), and the following robot configuration in the Viam app:

``` json
{
  "components": [
     {
      "depends_on": [],
      "model": "webcam",
      "name": "camera",
      "type": "camera",
      "attributes": {},
        "path": "change-this-with-your-own-camera-path"
      }
  ]
}
```
