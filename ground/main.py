import sys
import json
from machine import I2C, UART, Pin
from utime import sleep
from bme680 import *

onPin = Pin("LED", Pin.OUT)
bmeVcc = Pin(11, Pin.OUT)
bmeVcc.on()
bmeGND = Pin(14, Pin.OUT)
bmeGND.off()

bleVcc = Pin(3, Pin.OUT)
bleVcc.on()
BLEuart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))  # UART0 on GP0/GP1


i = I2C(id=0, scl=Pin(13), sda=Pin(12))
if len(i.scan()) != 1:
    print("no BME680 found on these pins. addrses", i.scan())
    sys.exit()

bme = BME680_I2C(i, address=i.scan()[0])


def send_at_command(command, response_timeout=0.1):
    BLEuart.write(command + "\r\n")
    sleep(response_timeout)
    if BLEuart.any():
        response = BLEuart.read().decode("utf-8").strip()
        print(f"Response: {response}")
    else:
        print("No response from BLE module.")


# send_at_command("+++")
# send_at_command("ATI")
# send_at_command("AT+GAPDEVNAME=GroundModuleBLE")
# send_at_command("AT+GATTADDSERVICE?")
# send_at_command("AT+GAPGETCONN")
# send_at_command("+++")


print("LED starts flashing...")
count = 0
while True:
    count += 1
    # print(bme.temperature, bme.humidity, bme.pressure, bme.gas)
    data = json.dumps(
        {
            # header: f"message #{}"
            "moduleID": 1,
            "moduleName": "Ground",
            "count": count,
            # "timestamp": str(datetime.now()),
            "temp": round(bme.temperature, 2),
            "humidity": round(bme.humidity, 2),
            "pressure": round(bme.pressure / 10, 2),
            "units": "°C, %, kPa",
        }
    )

    msg = f"[START]{data}[END]"
    BLEuart.write(msg)
    print(msg)

    onPin.high()
    sleep(0.2)
    onPin.low()
    sleep(0.8)
