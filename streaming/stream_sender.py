import socket
import threading
import time

import cv2
import imutils
from imagezmq import imagezmq
from imutils.video import VideoStream


class StreamSender(threading.Thread):

    def __init__(self, server_ip, is_pi):
        threading.Thread.__init__(self)
        self.daemon = True
        self.server_ip = server_ip
        self.is_pi = is_pi

    def run(self):
        sender = imagezmq.ImageSender(connect_to='tcp://{}:5555'.format(self.server_ip))
        host_name = socket.gethostname()

        if self.is_pi:
            vs = VideoStream(usePiCamera=True).start()
        else:
            vs = VideoStream(src=0).start()
        time.sleep(2)

        print("Started capturing and streaming video from camera")

        while True:
            frame = vs.read()
            frame = imutils.resize(frame, width=480)
            cv2.putText(frame, host_name, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            sender.send_image(host_name, frame)
