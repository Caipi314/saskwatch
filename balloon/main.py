# from datetime import datetime
import json
from machine import UART, Pin, ADC

# from bme680 import *
from time import sleep

onPin = Pin("LED", Pin.OUT)

bleVcc = Pin(3, Pin.OUT)
bleVcc.on()
BLEuart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))  # UART0 on GP0/GP1


def send_at_command(command, response_timeout=0.1):
    BLEuart.write(command + "\r\n")
    sleep(response_timeout)
    if BLEuart.any():
        response = BLEuart.read().decode("utf-8").strip()
        print(f"Response: {response}")
        return response
    else:
        print("No response from BLE module.")

adc = ADC(26)  # ADC0 corresponds to GP26 on Pico

def get_voltage(pin):
    return (pin.read_u16() * 3.3) / 65535  # Convert digital value to analog voltage

def wind_speed(voltage):
    return voltage  # Linear assumption, may need adjustment

solenoid_relay = Pin(16, Pin.OUT)  # GP16 as output
def trigger_pin(delay):
    solenoid_relay.value(1)
    sleep(delay)
    solenoid_relay.value(0)

# Define rotary encoder pins
DT_Pin = Pin(0, Pin.IN, Pin.PULL_UP)  # GP0 as input with pull-up
CLK_Pin = Pin(1, Pin.IN, Pin.PULL_UP)  # GP1 as input with pull-up

value = 0
previous_value = 1

def rotary_changed():
    global previous_value, value

    if previous_value != CLK_Pin.value():
        if CLK_Pin.value() == 0:
            if DT_Pin.value() == 0:
                value = (value - 1) % 20
                print("anti-clockwise", value)
            else:
                value = (value + 1) % 20
                print("clockwise", value)
        previous_value = CLK_Pin.value()


send_at_command("+++")
send_at_command("ATI")
send_at_command("AT+GAPDEVNAME=BalloonModuleBLE")
send_at_command("AT+GATTADDSERVICE?")
send_at_command("AT+GAPGETCONN")
send_at_command("+++")

# custom protocol:
# [START]...[END]

count = 0
while True:
    count += 1
    # data = json.dumps({"message": f"hello #{count}"})
    # msg = f"[START]{data}[END]"
    # BLEuart.write(msg)
    # print(msg)
    windSpeed = wind_speed()
    rotary_changed(get_voltage(adc))


    data = json.dumps(
        {"moduleID": 2, "moduleName": "Balloon", "count": count, "message": "hello", "Direction": value*18, "windspeed": windSpeed}
    )

    msg = f"[START]{data}[END]"
    BLEuart.write(msg)
    print(msg)

    onPin.high()
    sleep(0.2)
    onPin.low()
    sleep(0.8)
