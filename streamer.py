# USAGE
# python streamer.py --server-ip SERVER_IP
# OR
# python streamer.py

import socket
import time
from threading import Thread

import click
import imagezmq
from imutils.video import VideoStream


def validate_ip_address(ctx, param, value):
    if value != 'localhost':
        try:
            socket.inet_aton(value)
        except OSError:
            raise click.BadParameter('server ip must be a valid ip address')
    return value


def send_frames(server_ip, pi):
    sender = imagezmq.ImageSender(connect_to='tcp://{}:5555'.format(server_ip))
    device = socket.gethostname()

    if pi:
        vs = VideoStream(usePiCamera=True).start()
    else:
        vs = VideoStream(src=0).start()
    time.sleep(2.0)

    print("Started capturing and streaming video from camera")

    while True:
        frame = vs.read()
        # frame = imutils.resize(frame, width=320) to resize
        sender.send_image(device, frame)


@click.command(name='stream_camera')
@click.option('--server-ip', callback=validate_ip_address, default='localhost', show_default=True,
              help='ip address to stream the captured video to, localhost by default')
@click.option('--pi', is_flag=True,
              help="specifies that the streaming device is a raspberry pi")
def stream_camera(server_ip, pi):
    streaming_thread = Thread(target=send_frames, args=(server_ip, pi,))
    # daemon threads are terminated after main thread dies
    streaming_thread.daemon = True
    streaming_thread.start()

    # keep program alive while intercepting key interrupts
    while not time.sleep(1):
        pass


if __name__ == '__main__':
    stream_camera()
