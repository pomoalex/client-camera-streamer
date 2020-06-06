import multiprocessing
import threading
import time
from datetime import datetime

from streaming.stream_sender import StreamSender


class StreamSendHandler(threading.Thread):

    def __init__(self, server_ip, is_pi):
        threading.Thread.__init__(self)
        self.daemon = True
        self.shared_dict = multiprocessing.Manager().dict()
        self.server_ip = server_ip
        self.LIVENESS_CHECK_SECONDS = 5
        self.MAX_TIMEOUT = 10
        self.stream_sender = StreamSender(self.shared_dict, server_ip, is_pi)

    def run(self):
        self.stream_sender.start()
        streaming_start = datetime.now()
        while True:
            time.sleep(self.LIVENESS_CHECK_SECONDS)
            last_connection = self.shared_dict['connection']
            if last_connection is None:
                if (datetime.now() - streaming_start).seconds > self.MAX_TIMEOUT:
                    print("[ERROR] Could not connect to {}".format(self.server_ip))
                    break
            elif (datetime.now() - last_connection).seconds > self.MAX_TIMEOUT:
                print("[WARN] Lost connection to {} due to timeout".format(self.server_ip))
                break
