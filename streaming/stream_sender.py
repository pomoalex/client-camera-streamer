import socket
import time
from datetime import datetime
from multiprocessing import Process

import cv2
import imutils
from imagezmq import imagezmq
from imutils.video import VideoStream


class StreamSender(Process):

    def __init__(self, shared_dict, server_ip, is_pi, host_name):
        Process.__init__(self)
        self.shared_dict = shared_dict
        self.shared_dict['connection'] = None
        self.daemon = True
        self.server_ip = server_ip
        self.is_pi = is_pi
        self.host_name = host_name

    def run(self):
        try:
            host_name, sender = self.connect()
            if self.host_name is not None:
                host_name = self.host_name
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

        self.add_text(frame, host_name, (10, 10), (4, 4))

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
        _, frame = cv2.imencode('.jpg', frame, encode_param)

        return frame

    def add_text(self, frame, text, start_coord, padding):
        font = cv2.FONT_HERSHEY_PLAIN
        text_size = cv2.getTextSize(text, font, fontScale=1, thickness=1)[0]

        end_coord = (start_coord[0] + text_size[0] + padding[0], start_coord[1] + text_size[1] + padding[1])

        cv2.rectangle(frame, start_coord, end_coord, color=(255, 255, 255), thickness=-1)

        cv2.putText(frame, text,
                    org=(start_coord[0] + padding[0] // 2, start_coord[1] + text_size[1] + padding[1] // 2),
                    fontFace=cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1,
                    color=(0, 0, 0),
                    thickness=1)
