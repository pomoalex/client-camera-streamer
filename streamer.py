# USAGE
# python streamer.py --server-ip SERVER_IP
# OR
# python streamer.py

import socket
import time

import click

from streaming import StreamSendHandler


def validate_ip_address(ctx, param, value):
    if value != 'localhost':
        try:
            socket.inet_aton(value)
        except OSError:
            raise click.BadParameter('server ip must be a valid ip address')
    return value


@click.command(name='stream_camera')
@click.option('--server-ip', callback=validate_ip_address, default='localhost', show_default=True,
              help='ip address to stream the captured video to, localhost by default')
@click.option('--is-pi', is_flag=True,
              help="specifies that the streaming device is a raspberry pi")
def stream_camera(server_ip, is_pi):
    stream_send_handler = StreamSendHandler(server_ip, is_pi)
    stream_send_handler.start()

    # keep program alive while intercepting key interrupts
    while not time.sleep(5):
        if not stream_send_handler.is_alive():
            break


if __name__ == '__main__':
    stream_camera()
