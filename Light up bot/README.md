# Light up bot

This script configures 

an ultrasonic sensor to avoid walls and obstacles (via a sensor such as [ultrasonic sensor](https://www.amazon.com/Dorhea-Ultrasonic-Distance-Duemilanove-Rapsberry/dp/B07L68X65N/ref=sr_1_3?)).
It was created for [this workshop prompt](https://docs.google.com/document/d/1YTm0KlSHBQdgexX9Wt-B6mEeOzzF53plqihrrNkCc1M/edit).

It expects an kasa smart plug to be attached to a light source, and the following robot configuration in Viam app:

``` json
{
  "components": [
     {
      "depends_on": [],
      "model": "webcam",
      "name": "camera",
      "type": "camera",
      "attributes": {
        "debug": false,
        "height_px": 0,
        "path_pattern": "",
        "width_px": 0,
        "intrinsic_parameters": {
          "width_px": 0,
          "fx": 0,
          "fy": 0,
          "height_px": 0,
          "ppx": 0,
          "ppy": 0
        },
        "stream": "",
        "format": "",
        "distortion_parameters": {
          "rk1": 0,
          "rk2": 0,
          "rk3": 0,
          "tp1": 0,
          "tp2": 0
        },
        "path": "change-this-with-your-own-camera-path"
      }
    }
  ]
}
```

Note that the environment variables ROBOT_SECRET and ROBOT_ADDRESS are expected to be set.
