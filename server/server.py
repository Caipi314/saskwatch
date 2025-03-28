import asyncio
import json
from threading import Thread
import threading
from BLE import uart_terminal
from http.server import HTTPServer, BaseHTTPRequestHandler


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


latestData = [{"balloon module loading": True}, {"ground module loading": True}]
connected = False


def full_msg(msg):
    global latestData
    try:
        msgData = json.loads(msg)
        latestData[msgData["moduleID"] - 1] = msgData
        print("latestData", msgData)
    except:
        print(f"ERROR: {msg}")


# async def every(__seconds: float, func, *args, **kwargs):
#     while True:
#         func(*args, **kwargs)
#         await asyncio.sleep(__seconds)


#     await asyncio.sleep(5)
#     startReconnect()
#     # thread1.start()


def BLEThread(name):
    async def onDisconnect(name):
        thread.cancel()
        print(f"{name} disconnected")

    thread = threading.Thread(
        target=asyncio.run,
        args=(uart_terminal(full_msg, onDisconnect, name),),  # NEED BOTH WEIRD COMMAS
    )


def connect(thread):
    # try:
    try:
        thread.start()
    except Exception as e:
        print("thread err", e)
        return


names = ["GroundModuleBLE", "BalloonModuleBLE"]
connect(BLEThread(names[0]))
connect(BLEThread(names[1]))
# startReconnect(names[1])

# except:
#     return


# thread1 = threading.Thread(
#     target=asyncio.run,
#     args=(
#         uart_terminal(full_msg, onDisconnect, "GroundModuleBLE"),
#     ),  # NEED BOTH WEIRD COMMAS
# )


# thread1 = threading.Thread(
#     target=asyncio.run,
#     args=(
#         uart_terminal(full_msg, onDisconnect, "GroundModuleBLE"),
#     ),  # NEED BOTH WEIRD COMMAS
# )
# # thread2 = threading.Thread(
# #     target=asyncio.run,
# #     args=(
# #         uart_terminal(full_msg, setConnected, "BalloonModuleBLE"),
# #     ),  # NEED BOTH WEIRD COMMAS
# # )
# try:
#     thread1.start()
#     # thread2.start()
# except asyncio.CancelledError as e:
#     print(e)


httpd = HTTPServer(("", 3000), SimpleHTTPRequestHandler)
try:
    print("Listening at http://localhost:3000/")
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
