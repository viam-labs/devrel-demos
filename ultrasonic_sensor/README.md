# Ultrasonic workshop

This script configures an ultrasonic sensor to avoid walls and obstacles (via a sensor such as [ultrasonic sensor](https://www.amazon.com/Dorhea-Ultrasonic-Distance-Duemilanove-Rapsberry/dp/B07L68X65N/ref=sr_1_3?)).
It was created for [this workshop prompt](https://docs.google.com/document/d/1YTm0KlSHBQdgexX9Wt-B6mEeOzzF53plqihrrNkCc1M/edit).
It expects an ultrasonic sensor to be attached to a Raspberry Pi, pin 40 for trigger and pin 38 for echo, and the following robot configuration in Viam app:

``` json
{
  "components": [
      {
      "name": "ultrasonic",
      "type": "sensor",
      "model": "ultrasonic",
      "attributes": {
        "trigger_pin": "40",
        "echo_interrupt_pin": "38",
        "board": "local"
      },
      "depends_on": []
    }
  ]
}
```

Note that the environment variables ROBOT_API_KEY, ROBOT_API_KEY_ID, and ROBOT_ADDRESS are expected to be set.
