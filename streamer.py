# USAGE
# python client.py --server-ip SERVER_IP

import socket
import time

import click
import imagezmq
from imutils.video import VideoStream


def validate_ip_address(ctx, param, value):
    if value != 'localhost':
        try:
            socket.inet_aton(value)
        except OSError:
            raise click.BadParameter('server ip must be a valid ip address')


@click.command(name='stream_camera')
@click.option('--server-ip', 'server_ip', callback=validate_ip_address, default='localhost',
              help='ip address to stream the captured video to, localhost by default')
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
