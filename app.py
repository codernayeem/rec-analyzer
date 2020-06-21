from flask import Flask, Blueprint, render_template, redirect, request, session, Response, url_for
from colorama import init, Fore, Back
import socket, sys

init()
app = Flask(__name__, instance_relative_config=False, static_folder='.static', template_folder='.templates')


@app.route('/')
def index_view():
    return 'Hello World'

	
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

    print(f'\n\t ****  REC ANALYZER  ****\n')
    print(' * Host : ', host)
    print(' * Port : ', port)
    app.run(host=host, port=port, debug=True)
