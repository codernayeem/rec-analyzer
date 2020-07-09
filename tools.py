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
        'show_time_format': '%I:%M:%S %p',

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

    def get_filtered_records(self, rec_name, call_type, date_start, date_end, time_start, time_end, call_numbers):
        all_dates = sorted(get_folders(join(self.get('rec_folder'), rec_name)))

        date_start = get_valid_datetime(date_start, '%Y-%m-%d')
        date_end = get_valid_datetime(date_end, '%Y-%m-%d')
        time_start = get_valid_datetime(time_start, '%H:%M')
        time_end = get_valid_datetime(time_end, '%H:%M')


        if not date_start and not date_end:
            wanted_dates = all_dates
        else:
            wanted_dates = []
            for i in all_dates:
                i_date = get_valid_datetime(i, self.get('folder_date_format'))
                if i_date:
                    if not ((date_start and date_start > i_date) or (date_end and date_end < i_date)):
                        wanted_dates.append(i)

        all_records = []

        for i_date in wanted_dates:
            for i in self.get_records(rec_name, i_date):
                if (call_type == '1' and i['call_type'] == 'OUT') or (call_type == '2' and i['call_type'] == 'IN'):
                    continue
                if call_numbers and i['call_number'] not in call_numbers:
                    continue
                if time_start or time_end:
                    if (time_start and time_start > i['call_time_object']) or (time_end and time_end < i['call_time_object']):
                        continue

                i['call_date'] = i_date
                all_records.append(i)

        return all_records

    def get_files_size(self, files):
        i = 0
        for ii in files:
            i += ii['file_size']
        return i

    def check_password(self, ps):
        return self.data['password'] == str(ps)


def get_valid_datetime(datetime_string, _format):
    try:
        return datetime.strptime(datetime_string, _format)
    except:
        return None


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
