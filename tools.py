from os.path import join, isfile, isdir
from os import listdir
from pathlib import Path
from datetime import datetime 
import time, base64


def get_splited_by_comma(s):
    if s:
        s = str(s).split(',')
        return [i.strip() for i in s if i.strip()]
    return []


def is_valid_file(fl):
    if fl is not None:
        p = Path(fl)
        if p.exists() and p.is_file():
            return True
    return False


def sizeSince(byte):
    byte = int(byte)
    if byte < 1024:
        return f'{byte} B'
    elif byte < 1024**2:
        byte = byte / (1024)
        s = " KB"
    elif byte < 1024**3:
        byte = byte / (1024**2)
        s = " MB"
    else:
        byte = byte / (1024**3)
        s = " GB"
    byte = "{0:.2f}".format(byte)
    return byte + s


def get_folders(pth):
    return [f for f in listdir(pth) if isdir(join(pth, f))]


def get_files(pth):
    return [f for f in listdir(pth) if isfile(join(pth, f))]


def encode64(s):
    if s:
        try:
            return base64.encodebytes(str(s).encode()).decode()
        except:
            pass
    return None


def decode64(s):
    if s:
        try:
            return base64.decodebytes(str(s).encode()).decode()
        except:
            pass
    return None
