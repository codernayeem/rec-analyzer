from flask import Flask, Blueprint, render_template, redirect, request, session, Response, url_for
from colorama import init, Fore, Back
import socket, sys, config as cfg
from tools import AppData, get_folders, join

init()
app = Flask(__name__, instance_relative_config=False, static_folder='.static', template_folder='.templates')
appData = AppData()

@app.route('/')
def index_view():
    global appData
    folders = sorted(get_folders(appData.get('rec_folder')))
    return render_template('index.html', rec_names=folders, count=len(folders))

@app.route('/map/<rec_name>/')
def map_go_view(rec_name):
    global appData
    rec_folder = appData.get('rec_folder')
    if not rec_name or not rec_name in get_folders(rec_folder):
        return redirect('/')
    
    all_dates = sorted(get_folders(join(rec_folder, rec_name)))
    return render_template('map.html', rec_name=rec_name, all_dates=all_dates, count=len(all_dates))

if __name__ == "__main__":
    host = socket.gethostbyname(socket.gethostname())
    port = 1999
    if len(sys.argv) == 2:
        host = sys.argv[1]
    elif len(sys.argv) == 3:
        if sys.argv[1] != '*':
            host = sys.argv[1]
        port = int(sys.argv[2])
    elif len(sys.argv) > 3:
        print('\n[+] - Too Many Parameters')
        exit(1)

    print(f'\n\t ****  REC ANALYZER v{cfg.VERSION}  ****\n')
    print(' * Host : ', host)
    print(' * Port : ', port)
    app.run(host=host, port=port, debug=True)
