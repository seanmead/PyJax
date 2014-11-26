"""
Created on Oct 1, 2014

@author: Sean Mead
"""


import os
import sys
import time
import urllib
import inspect
import platform
import struct
import subprocess


def get_address():
    for interface_name in get_interfaces():
        interface = get_interface(interface_name)
        if 'Windows' in platform.system():
            return interface.get('IP Address')
        else:
            if interface.get('status') == 'active':
                net = interface.get('inet')
                if net:
                    return net


def get_interfaces():
    if 'Windows' in platform.system():
        interfaces = subprocess.check_output('netsh interface show interface', shell=True).split('\n')[3:]
        return [item.split('     ')[-1].strip() for item in interfaces if item.strip() != '']
    else:
        return subprocess.check_output('ifconfig -lu', shell=True).split(' ')


def get_interface(interface_name):
    interface = {'name': interface_name}
    if 'Windows' in platform.system():
        items = subprocess.check_output('netsh interface ip show addresses %s' % interface_name, shell=True).split('\n')
        items = [item.strip().split(':') for item in items[2:] if item.strip() != '']
        for item in items:
            try:
                interface.update({item[0].strip(): item[1].strip()})
            except IndexError:
                pass
    else:
        for line in subprocess.check_output('ifconfig %s' % interface_name, shell=True).split('\n'):
            if '\t' in line:
                line = line.replace('\t', '')
                line = line.split(' ', 1)
                if len(line) > 1:
                    items = str(line[1]).split(' ')
                    interface.update({line[0].replace(':', '').strip(): items[0].strip()})
                    count = 0
                    for index in range(0, len(items)):
                        try:
                            interface.update({items[count].strip(): items[count + 1].strip()})
                        except IndexError:
                            pass
                        count += 2
    return interface


def route_path():
    """
    Change the os directory to the current site.
    """
    abs_path = os.path.realpath(inspect.getfile(inspect.currentframe()))
    os.chdir(os.path.abspath(os.path.join(abs_path, os.pardir)))


def decode_socket(stream):
    """
    Decode a WebSocket.
    :param stream: Read in socket stream
    :return: Decoded stream
    """
    byte_array = [ord(character) for character in stream]
    data_length = byte_array[1] & 127
    index_first_mask = 2
    if data_length == 126:
        index_first_mask = 4
    elif data_length == 127:
        index_first_mask = 10
    masks = [m for m in byte_array[index_first_mask: index_first_mask + 4]]
    index_first_data_byte = index_first_mask + 4
    decoded_chars = []
    i = index_first_data_byte
    j = 0
    while i < len(byte_array):
        decoded_chars.append(chr(byte_array[i] ^ masks[j % 4]))
        i += 1
        j += 1
    return ''.join(decoded_chars)


def encode_socket(s):
        """
        WebSocket encode a string.
        :param s: String to encode
        :return: Encoded string.
        """
        message = ""
        b1 = 0x80
        payload = None
        if type(s) == unicode:
            b1 |= 0x01
            payload = s.encode("UTF8")
        elif type(s) == str:
            b1 |= 0x02
            payload = s

        message += chr(b1)

        b2 = 0
        length = len(payload)
        if length < 126:
            b2 |= length
            message += chr(b2)
        elif length < (2 ** 16) - 1:
            b2 |= 126
            message += chr(b2)
            l = struct.pack(">H", length)
            message += l
        else:
            l = struct.pack(">Q", length)
            b2 |= 127
            message += chr(b2)
            message += l

        message += payload

        return message


def clear_screen():
    """
    Clear the terminal/cmd screen.
    """
    if 'Windows' in platform.system():
        os.system('cls')
    else:
        os.system('clear')


def terminate():
    """
    Destroy all pythons.
    """
    if 'Windows' in platform.system():
        os.system('taskkill -f -im python.exe')
    else:
        os.system('sudo pkill -9 Python')


def get_epoch(date):
    return int(time.mktime(time.strptime(str(date), '%Y-%m-%d %H:%M:%S')))


def human_time(epoch):
    """
    Return a human readable epoch.
    :param epoch:
    """
    return time.strftime("%a, %d %b %Y %I:%M:%S %p", time.localtime(epoch))


def get_item(data, item):
    """
    Get a data item specified by the Html Get format.
    :param data: full string
    :param item: item to find
    """
    op = data[data.index(item):]
    op = op.split('\n')[0].split('=')[1].split('&')[0]
    return strip_item(op)


def strip_item(item):
    """
    Decode a url string.
    :param item: String to strip
    """
    return urllib.unquote(item).decode('utf8').replace('+', ' ').replace('../', '').replace('./', '').strip()


def split_extension(filename):
    """
    Returns the name, ext of the given filename.
    :param filename: filename to split
    """
    name, ext = os.path.splitext(filename)
    ext = ext.replace(".", "")
    return name, ext


def get_files(path):
    """
    Parses through a directory and finds all files.
    :rtype : list
    :param path: path to parent of the files
    """
    try:
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.startswith('.')]
    except OSError:
        return []


def print_delay(text):
    """
    Delayed printer.
    :param text:
    """
    for char in text:
        print_nln(char)
    time.sleep(0.5)


def print_nln(string, delay=True):
        """
        Print without new line.
        :param string:
        :param delay:
        """
        sys.stdout.write(string)
        sys.stdout.flush()
        if delay:
            time.sleep(0.1)


class SuppressError(object):
    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])


