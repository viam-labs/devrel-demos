# Candy machine actuator and sensor workshop

This script senses a GPIO pin changing state (via a sensor such as an [infrared obstacle avoidance sensor](https://www.amazon.com/HiLetgo-Infrared-Avoidance-Reflective-Photoelectric/dp/B07W97H2WS)) and activates a stepper motor.
It was created for [this workshop prompt](https://docs.google.com/document/d/1hjI9_Ubdz2aDzBvj8GrPfG2kBaUQC7tOXY1bfYC11Uo/edit?usp=sharing).
It expects a GPIO sensor to be attached to pin 37, and the following robot configuration:

``` json
{
  "components": [
    {
      "model": "gpiostepper",
      "attributes": {
        "pins": {
          "step": "16",
          "dir": "15",
          "en_low": "18"
        },
        "board": "pi",
        "ticks_per_rotation": 400,
        "stepper_delay_usec": 40
      },
      "depends_on": [],
      "name": "stepper",
      "type": "motor"
    },
    {
      "type": "board",
      "model": "pi",
      "attributes": {},
      "depends_on": [],
      "name": "pi"
    }
  ]
}
```

Note that the environment variables ROBOT_API_KEY and ROBOT_API_KEY_ID are expected to be set - these can be retrieved from your robot's 'CODE SAMPLE' tab.
