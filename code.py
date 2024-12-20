# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Pico and Pico W board support


import supervisor

import time
import digitalio
from board import *
import board
from duckyinpython import *
if(board.board_id == 'raspberry_pi_pico_w'):
    import wifi
    from webapp import *

# Settings
Autoinject=False

# init run button. This is only needed when Autoinject = False
if (Autoinject==False):
    runButton_pin = DigitalInOut(GP15) # defaults to input
    runButton_pin.pull = Pull.UP       # turn on internal pull-up resistor
    runButton =  Debouncer(runButton_pin)

# sleep at the start to allow the device to be recognized by the host computer
time.sleep(.5)

def startWiFi():
    import ipaddress
    # Get wifi details and more from a secrets.py file
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise

    print("Connect wifi")
    #wifi.radio.connect(secrets['ssid'],secrets['password'])
    wifi.radio.start_ap(secrets['ssid'],secrets['password'])

    HOST = repr(wifi.radio.ipv4_address_ap)
    PORT = 80        # Port to listen on
    print(HOST,PORT)

# turn off automatically reloading when files are written to the pico
#supervisor.disable_autoreload()
supervisor.runtime.autoreload = False

if(board.board_id == 'raspberry_pi_pico'):
    led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
elif(board.board_id == 'raspberry_pi_pico_w'):
    led = digitalio.DigitalInOut(board.LED)
    led.switch_to_output()

led_state = False

async def main_loop():
    global led,button1

    button_task = asyncio.create_task(monitor_buttons(button1))
    if(board.board_id == 'raspberry_pi_pico_w'):
        pico_led_task = asyncio.create_task(blink_pico_w_led(led))
        print("Starting Wifi")
        startWiFi()
        print("Starting Web Service")
        webservice_task = asyncio.create_task(startWebService())
        await asyncio.gather(pico_led_task, button_task, webservice_task)
    else:
        pico_led_task = asyncio.create_task(blink_pico_led(led))
        await asyncio.gather(pico_led_task, button_task)

asyncio.run(main_loop())

progStatus = False
progStatus = getProgrammingStatus() # Get programmingstatus
print("progStatus", progStatus)

if(progStatus == False and Autoinject == True):            # Checks if brogramming pins are shorted
    print("Finding payload")
    # not in setup mode, inject the payload
    payload = selectPayload()
    print("Running ", payload)
    runScript(payload)              # Run the payload
    print("Done")
elif:
    print("Going into button mode")
    while True:
        # Check if button is pressed
        pressed = digitalio.DigitalInOut(GP0)
        pressed.switch_to_input(pull=digitalio.Pull.UP)
        pressed = not runButton_pin.value
        if pressed:
            print("Run button was pressed, injecting payload")
            payload = selectPayload()
            print("Running ", payload)
            runScript(payload) 
            print("Done")
        time.sleep(0.2)
else:
    print("It went to shit")
        

