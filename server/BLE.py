import asyncio
import sys
from itertools import count, takewhile
from typing import Iterator

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
# BLEAddress = "F4:FB:CE:E2:D8:33"
# BLEName = "BalloonModuleBLE"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


buffer = ""


async def uart_terminal(onMsg, onDisconnect=lambda x: x, BLEName="not a real device"):
    print(f"Looking for device with name {BLEName}")
    # setConnected(False)
    device = await BleakScanner.find_device_by_filter(
        timeout=30, filterfunc=lambda d, adv: adv.local_name == BLEName
    )
    # device.but

    if device is None:
        print("no matching device found")
        sys.exit(1)

    def handle_disconnect(_: BleakClient):
        # print("buffer", buffer)
        print("Device was disconnected, goodbye.")
        # cancelling all tasks effectively ends the program
        onDisconnect(BLEName)
        # for task in asyncio.all_tasks():
        #     task.cancel()

    def handle_rx(_: BleakGATTCharacteristic, data):
        # print("an rx", data.decode("utf-8"))
        global buffer
        startsMsg = "[START]"
        endsMsg = "[END]"
        data = data.decode("utf-8")

        buffer += data

        # process buffer
        start = buffer.find(startsMsg)
        end = buffer.find(endsMsg)
        if start != 1 and end != -1 and end > start:
            latestMsg = buffer[start + len(startsMsg) : end]

            buffer = buffer[end + len(endsMsg) :]
            onMsg(latestMsg)

    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)

        loop = asyncio.get_running_loop()
        while True:
            _data = await loop.run_in_executor(None, sys.stdin.buffer.readline)
