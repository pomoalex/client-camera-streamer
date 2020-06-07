import socket
import sys
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
        try:
            host_name, sender = self.connect()
            video_stream = self.get_video_stream()

            logged_start = False
            while True:
                frame = self.read_and_process_frame(video_stream, host_name)
                sender.send_image(host_name, frame)
                self.shared_dict['connection'] = datetime.now()
                if not logged_start:
                    print('[INFO] Started capturing and streaming video from camera')
                    logged_start = True

        except KeyboardInterrupt:
            pass

    def get_video_stream(self):
        if self.is_pi:
            video_stream = VideoStream(usePiCamera=True).start()
        else:
            video_stream = VideoStream(src=0).start()
        time.sleep(2)
        return video_stream

    def connect(self):
        address = 'tcp://{}:5555'.format(self.server_ip)
        sender = imagezmq.ImageSender(connect_to=address)
        host_name = socket.gethostname()
        print('[INFO] Connecting to {}'.format(address))
        return host_name, sender

    def read_and_process_frame(self, video_stream, host_name):
        frame = video_stream.read()
        frame = imutils.resize(frame, width=480)

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
        _, frame = cv2.imencode('.jpg', frame, encode_param)

        cv2.putText(frame, host_name, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        return frame
