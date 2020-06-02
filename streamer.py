# USAGE
# python streamer.py --server-ip SERVER_IP

import socket
import time

import click
import imagezmq
from imutils.video import VideoStream


@click.command()
@click.option('--server-ip', 'server_ip', required=True,
              help='ip address to stream the captured video to')
@click.option('--pi', is_flag=True,
              help="specifies that the streaming device is a raspberry pi")
def stream_camera(server_ip, pi):
    sender = imagezmq.ImageSender(connect_to='tcp://{}:5555'.format(server_ip))
    device = socket.gethostname()

    if pi:
        vs = VideoStream(usePiCamera=True).start()
    else:
        vs = VideoStream(src=0).start()

    time.sleep(2.0)

    while True:
        frame = vs.read()
        # frame = imutils.resize(frame, width=320) to resize
        sender.send_image(device, frame)


if __name__ == '__main__':
    stream_camera()
