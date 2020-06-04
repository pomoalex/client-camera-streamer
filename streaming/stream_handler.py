import threading
import time
from datetime import datetime

from streaming.stream_sender import StreamSender


class StreamSendHandler(threading.Thread):

    def __init__(self, server_ip, is_pi):
        threading.Thread.__init__(self)
        self.daemon = True
        self.lock = threading.Lock()
        self.streaming_details = [False, None]
        self.server_ip = server_ip
        self.LIVENESS_CHECK_SECONDS = 5
        self.MAX_INACTIVITY = 3
        self.stream_sender = StreamSender(self.lock, self.streaming_details, server_ip, is_pi)

    def run(self):
        self.stream_sender.start()
        while True:
            time.sleep(self.LIVENESS_CHECK_SECONDS)
            with self.lock:
                if self.streaming_details[0]:
                    if self.streaming_details[1] is None:
                        print("[ERROR] Could not connect to {}".format(self.server_ip))
                        break

                    if (datetime.now() - self.streaming_details[1]).seconds > self.MAX_INACTIVITY:
                        print("[WARN] Lost connection to {}".format(self.server_ip))
                        break
