import json
from machine import UART, Pin

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


# send_at_command("+++")
# send_at_command("ATI")
# send_at_command("AT+GAPDEVNAME=BalloonModuleBLE")
# send_at_command("AT+GATTADDSERVICE?")
# send_at_command("AT+GAPGETCONN")
# send_at_command("+++")

# custom protocol:
# [START]...[END]

count = 0
while True:
    count += 1
    data = json.dumps(
        {"moduleID": 2, "moduleName": "Balloon", "count": count, "windspeed": 6}
    )

    msg = f"[START]{data}[END]"
    BLEuart.write(msg)
    print(msg)

    onPin.high()
    sleep(0.2)
    onPin.low()
    sleep(0.8)
