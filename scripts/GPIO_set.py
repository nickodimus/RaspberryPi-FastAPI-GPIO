#!/usr/bin/env python3

# GPIO_set.py

# GPIO gpios Set Already
#   gpio    relay
#   04      Transfer Switch SSR
#   17      Unasigned - test GPIO
#   27      1
#   21      2
#   13      3
#   26      4 victron battery charger



import time
import argparse
import RPi.GPIO as GPIO
from sorcery import dict_of

global status

def main(gpio,type,state):
    """
    Function to set the GPIO pin type and state, and retrieve the current value of the GPIO pin.

    Args:
        gpio: The GPIO pin number.
        type: The type of the GPIO pin (0 for input, 1 for output).
        state: The state of the GPIO pin ("low" for 0, "high" for 1).

    Returns:
        status: A dictionary containing the GPIO pin number, type, and state.
    """
    if type == 0:
        type = GPIO.IN
    else:
        type = GPIO.OUT

    if state == "low":
        state = 0
    else:
        state = 1

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio, type)
    GPIO.output(gpio, state)
    GPIO.remove_event_detect(gpio)
    #state = GPIO.input(gpio)
    print('current value of gpio', gpio, 'is', GPIO.input(gpio))
    
    status = dict_of(gpio, type, state)
    print (status)
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script that changes a specific GPIO's type and state from CMD"
    )
    parser.add_argument("--gpio", required=True, type=int)
    parser.add_argument("--type", required=True, type=str)
    parser.add_argument("--state", required=True, type=str)
    args = parser.parse_args()

    gpio = args.gpio
    type = args.type
    state = args.state

    main(gpio,type,state)