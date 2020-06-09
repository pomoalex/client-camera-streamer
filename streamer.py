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


def validate_connection_retries(ctx, param, value):
    if type(value) != int:
        if value != -1 and value < 0:
            raise click.BadParameter('connection-retries must be an integer number (>=0)')
    return value


@click.command(name='stream_camera')
@click.option('--server-ip', callback=validate_ip_address, default='localhost', show_default=True,
              help='ip address to stream the captured video to')
@click.option('--connection-retries', callback=validate_connection_retries, default=-1, show_default=True,
              help='(positive)number of server connection attempts, -1 for infinite tries')
@click.option('--host-name',
              help='camera screen label, default is device name')
@click.option('--is-pi', is_flag=True,
              help="specifies that the streaming device is a raspberry pi")
def stream_camera(server_ip, connection_retries, is_pi, host_name=None):
    try:
        stream_handler = StreamSendHandler(server_ip, connection_retries, is_pi, host_name)
        stream_handler.start()
        while stream_handler.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print('[INFO] Graceful shutdown due to KeyboardInterrupt')


if __name__ == '__main__':
    stream_camera()
