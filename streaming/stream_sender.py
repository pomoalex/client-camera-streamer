import socket
import time
from datetime import datetime
from multiprocessing import Process

import cv2
import imutils
from imagezmq import imagezmq
from imutils.video import VideoStream


class StreamSender(Process):

    def __init__(self, shared_dict, server_ip, is_pi):
        Process.__init__(self)
        self.shared_dict = shared_dict
        self.shared_dict['connection'] = None
        self.daemon = True
        self.server_ip = server_ip
        self.is_pi = is_pi

    def run(self):
        address = 'tcp://{}:5555'.format(self.server_ip)
        sender = imagezmq.ImageSender(connect_to=address)
        host_name = socket.gethostname()
        print('[INFO] Connecting to {}'.format(address))

        if self.is_pi:
            vs = VideoStream(usePiCamera=True).start()
        else:
            vs = VideoStream(src=0).start()
        time.sleep(2)

        print('[INFO] Started capturing and streaming video from camera')

        while True:
            frame = vs.read()
            frame = imutils.resize(frame, width=480)
            cv2.putText(frame, host_name, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            sender.send_image(host_name, frame)
            self.shared_dict['connection'] = datetime.now()
