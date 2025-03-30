import asyncio
import json
from threading import Thread
import threading
from BLE import uart_terminal
from http.server import HTTPServer, BaseHTTPRequestHandler

from FWI import FWI


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"

        if self.path == "/data":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(latestData), "utf-8"))
            return

        if self.path == "/end":
            httpd.server_close()

        if not self.path.startswith("/static/"):
            self.path = "/static" + self.path

        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(file_to_open, "utf-8"))
        except:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"404 - Not Found")


latestData = [
    {"FWI": None},
    {"balloon": False, "loading": True},
    {"ground": False, "loading": True},
]
connected = False

fwi = FWI(month=4)


def full_msg(msg):
    global latestData
    msgData = {}
    try:
        msgData = json.loads(msg)
    except Exception as e:
        print(e)
        print(f"ERROR: {msg}")
        return

    latestData[msgData["moduleID"]] = msgData
    print("latestData", msgData)

    if "loading" in latestData[1] or "loading" in latestData[2]:
        print("not enough data for FWI")
        return
    # T, H, W, r_0
    T = latestData[1]["temp"]
    H = latestData[1]["humidity"]
    W = latestData[2]["windspeed"]
    r_0 = latestData[1]["water"]
    newFwi = fwi.addDay(T, H, W, r_0)
    latestData[0]["FWI"] = newFwi


def BLEThread(name):
    async def onDisconnect(name):
        thread.cancel()
        print(f"{name} disconnected")

    thread = threading.Thread(
        target=asyncio.run,
        args=(uart_terminal(full_msg, onDisconnect, name),),  # NEED BOTH WEIRD COMMAS
    )
    return thread


def connect(thread):
    try:
        thread.start()
    except Exception as e:
        print("thread err", e)
        return


names = ["GroundModuleBLE", "BalloonModuleBLE"]
connect(BLEThread(names[0]))
connect(BLEThread(names[1]))

httpd = HTTPServer(("", 3000), SimpleHTTPRequestHandler)
try:
    print("Listening at http://localhost:3000/")
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
