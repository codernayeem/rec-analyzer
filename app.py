from flask import Flask, Blueprint, render_template, redirect, request, session, Response, url_for, send_from_directory
from colorama import init, Fore, Back
import socket, sys, config as cfg
from tools import AppData, get_folders, join, sizeSince, encode64, decode64, is_valid_file, get_splited_by_comma
from functools import wraps
import json

init()
app = Flask(__name__, instance_relative_config=False, static_folder='.static', template_folder='.templates')
app.config.from_object('config.Config')
appData = AppData()


@app.context_processor
def inject_common_data():
    return dict(encode64=encode64, decode64=decode64, sizeSince=sizeSince, logged_in=session.get('logged_in'))

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if session.get('logged_in'):
            return func(*args, **kwargs)
        return redirect('/login')
    return decorated_view

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if session.get('logged_in'):
        return redirect(request.args.get('next') or '/')
    if request.method == 'GET':
        error = session.get('error_login')
        if error:
            session['error_login'] = None
        return render_template('login.html', error=error)

    if appData.check_password(decode64(request.form.get('data'))):
        session['logged_in'] = True
        return redirect(request.args.get('next') or '/')

    session['error_login'] = 'Incorrect username or password'
    return redirect('/login')

@app.route("/logout")
@login_required
def logout():
    session['logged_in'] = False
    return redirect('/login')

@app.route('/')
@login_required
def index_view():
    global appData
    folders = sorted(get_folders(appData.get('rec_folder')))
    return render_template('index.html', rec_names=folders, count=len(folders))

@app.route('/map/<rec_name>/')
@app.route('/map/<rec_name>/<rec_date>')
@login_required
def map_go_view(rec_name, rec_date=None):
    rec_name = decode64(rec_name)
    rec_date = decode64(rec_date)

    rec_folder = appData.get('rec_folder')
    if not rec_name or not rec_name in get_folders(rec_folder):
        return redirect('/')
    
    all_dates = sorted(get_folders(join(rec_folder, rec_name)))

    if rec_date:
        if rec_date in all_dates:
            date_index = all_dates.index(rec_date)
            old_date, next_date = None, None
            if date_index != 0:
                old_date = all_dates[date_index-1]
            if date_index != len(all_dates) - 1:
                next_date = all_dates[date_index+1]

            all_records = appData.get_records(rec_name, rec_date)
            all_records.sort(key=lambda i: i['call_time_object'], reverse=False)

            return render_template('records.html', rec_name=rec_name, size=appData.get_files_size(all_records), records=all_records, total=len(all_records), date=rec_date, old_date=old_date, next_date=next_date)
        else:
            return redirect('/map/'+rec_name)

    return render_template('map.html', rec_name=rec_name, all_dates=all_dates, count=len(all_dates))

@app.route('/filter')
@login_required
def filter_view():
    rec_names = sorted(get_folders(appData.get('rec_folder')))

    error = session.get('error_filter')
    if error:
        session['error_filter'] = None

    return render_template('filter.html', rec_names=rec_names, rec_name_count=len(rec_names), error=error)

@app.route('/filter_result', methods=['GET', 'POST'])
@login_required
def filter_result_view(encoded_filter_data=None):
    rec_folder = appData.get('rec_folder')

    if request.method == 'POST':
        rec_name = decode64(request.form.get('target'))
        call_type = request.form.get('call_type')
        date_start = request.form.get('date_start')
        date_end = request.form.get('date_end')
        time_start = request.form.get('time_start')
        time_end = request.form.get('time_end')
        call_numbers = get_splited_by_comma(request.form.get('call_numbers'))

        if not rec_name or rec_name not in get_folders(rec_folder) or call_type not in ('0', '1', '2'):
            session['error_filter'] = 'Please, give correct inputs.'
            return redirect(url_for('filter_view'))

        encoded_json_data = encode64(json.dumps(dict(
            rec_name=encode64(rec_name),
            call_type=call_type,
            date_start=date_start,
            date_end=date_end,
            time_start=time_start,
            time_end=time_end,
            call_numbers=call_numbers
            )))
        
        return redirect(url_for('filter_result_view', filter_data=encoded_json_data))

    encoded_filter_data = request.args.get('filter_data')
    if encoded_filter_data:
        try:
            filter_data = json.loads(decode64(encoded_filter_data))
            if filter_data.get('rec_name'):
                filter_data['rec_name'] = decode64(filter_data['rec_name'])
        except:
            filter_data = {}

        if filter_data and filter_data.get('rec_name') in get_folders(rec_folder) and filter_data.get('call_type') in ('0', '1', '2'):
            
            all_records = appData.get_filtered_records(filter_data.get('rec_name'), filter_data.get('call_type'), filter_data.get('date_start'), filter_data.get('date_end'), filter_data.get('time_start'), filter_data.get('time_end'), filter_data.get('call_numbers'))
            total_count = len(all_records)
            
            if total_count == 0:
                session['error_filter'] = 'No records found for that filter'
                return redirect(url_for('filter_view'))
            
            total_page = total_count // 30
            total_page += 0 if total_count % 30 == 0 else 1

            c_page = request.args.get('page')
            if c_page:
                try:
                    c_page = int(str(c_page))
                    if c_page > total_page:
                        c_page = total_page
                except:
                    c_page = 1
            else:
                c_page = 1

            item_per_page = 30
            if c_page == total_page:
                last_page_count = total_count - ((total_count // item_per_page) * item_per_page)
                last_page_count = item_per_page if last_page_count == 0 else last_page_count
                all_records = all_records[(c_page-1)*item_per_page:(c_page-1)*item_per_page+last_page_count]
            else:
                all_records = all_records[(c_page-1)*item_per_page:(c_page-1)*item_per_page+item_per_page]

            total_count = len(all_records)
            total_size_byte = sum([i['file_size'] for i in all_records])

            return render_template('filter_result.html', records=all_records, total_count=total_count, total_size=total_size_byte, rec_name=filter_data.get('rec_name'), c_page=c_page, total_page=total_page, filter_code=encoded_filter_data)

    session['error_filter'] = 'Please, give correct inputs.'
    return redirect(url_for('filter_view'))

@app.route('/file')
def download_view():
    if not session.get('logged_in'):
        return Response(status=403)
    try:
        fl, name, date = decode64(request.args.get('fl')), decode64(request.args.get('name')), decode64(request.args.get('date'))
        if fl and name and date and is_valid_file(join(appData.get('rec_folder'), name, date, fl)):
            return send_from_directory(join(appData.get('rec_folder'), name, date), fl, as_attachment=True)
    except:
        pass
    return Response(status=404)

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
