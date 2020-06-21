from flask import Flask, Blueprint, render_template, redirect, request, session, Response, url_for
from colorama import init, Fore, Back
import socket, sys

init()
app = Flask(__name__, instance_relative_config=False, static_folder='.static', template_folder='.templates')


@app.route('/')
def index_view():
    return 'Hello World'

	
if __name__ == "__main__":
    print(f'\n\t ****  REC ANALYZER  ****\n')
    app.run(host='localhost', port=7000, debug=True)
