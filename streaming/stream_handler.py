import multiprocessing
import sys
import threading
import time
from datetime import datetime

from streaming.stream_sender import StreamSender


class StreamSendHandler(threading.Thread):

    def __init__(self, server_ip, connection_retries, is_pi, host_name):
        threading.Thread.__init__(self)
        self.server_ip = server_ip
        self.is_pi = is_pi
        self.host_name = host_name
        self.max_connection_retries = connection_retries
        self.connection_retries = 0
        self.shared_dict = multiprocessing.Manager().dict()
        self.LIVENESS_CHECK_SECONDS = 5
        self.MAX_TIMEOUT = 5
        self.stream_sender = None
        self.stream_launch_time = None

    def run(self):
        self.start_streaming()
        while True:
            time.sleep(self.LIVENESS_CHECK_SECONDS)
            last_connection = self.get_last_connection()
            if last_connection is None:
                if (datetime.now() - self.stream_launch_time).seconds > self.MAX_TIMEOUT:
                    print("[ERROR] Could not connect to {}".format(self.server_ip))
                    self.restart_streaming()
            elif (datetime.now() - last_connection).seconds > self.MAX_TIMEOUT:
                print("[WARN] Lost connection to {} due to timeout".format(self.server_ip))
                self.restart_streaming()

    def start_streaming(self):
        self.stream_sender = StreamSender(self.shared_dict, self.server_ip, self.is_pi, self.host_name)
        self.stream_sender.start()
        self.stream_launch_time = datetime.now()

    def restart_streaming(self):
        self.connection_retries += 1
        if self.max_connection_retries == -1 or self.connection_retries <= self.max_connection_retries:
            print('[INFO] Retrying connection. Retry no. {}'.format(self.connection_retries))
            self.stream_sender.terminate()
            self.stream_sender.join()
            self.start_streaming()
        else:
            sys.exit()

    def get_last_connection(self):
        try:
            return self.shared_dict['connection']
        except BrokenPipeError:
            sys.exit()
