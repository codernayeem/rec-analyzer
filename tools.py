from os.path import join, isfile, isdir, getsize, sep
from os import listdir
from pathlib import Path
from datetime import datetime 
import time, base64


class AppData:
    data = {
        'folder_date_format': '%Y-%m-%d',
        'show_date_format': '%d/%m/%Y',
        'file_time_format': '%H-%M-%S',
        'show_time_format': '%h:%M:%S %p',

        'rec_folder': join('DATA', 'REC'),
        'password': '123' # default password
    }

    def __init__(self):
        create_folder(self.get('rec_folder'))

    def get(self, key, defult=None):
        return self.data.get(key, defult)

    def set_data(self, key, value):
        self.data[key] = value
        
    def get_records(self, rec_name, wanted_date):
        all_records= []

        for i in get_files(join(self.get('rec_folder'), rec_name, wanted_date)):
            splited = i.split('_')
            if len(splited) == 4:
                a_record = {}
                a_record['file_path'] = join(self.get('rec_folder'), rec_name, wanted_date, i)
                a_record['file_name'] = i
                a_record['file_size'] = getsize(a_record['file_path'])
                try:
                    a_record['call_time_object'] = datetime.strptime(splited[1], self.get('file_time_format'))
                except:
                    continue
                a_record['call_time'] = datetime.strftime(a_record['call_time_object'], self.get('show_time_format'))
                a_record['call_type'] = splited[2]
                a_record['call_number'] = splited[3].replace('+880', '0').replace('.amr', '').replace('.mp3', '').replace('.m4a', '').replace('.acc', '').replace('.ogg', '').replace('x', '*')
                
                all_records.append(a_record)
        return all_records

    def get_files_size(self, files):
        i = 0
        for ii in files:
            i += ii['file_size']
        return i

    def check_password(self, ps):
        return self.data['password'] == str(ps)


def create_folder(pth):
    s = ''
    for i in pth.split(sep):
        s = join(s, i)
        try:
            Path(s).mkdir()
        except:
            pass


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
