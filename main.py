import json
from datetime import datetime
from pytz import timezone, all_timezones, utc
from wsgiref.simple_server import make_server

def application(environ, start_response):

    path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD', 'GET')

    if method == 'GET' and path.startswith('/'):
        tz_name = path[1:] or 'GMT'
        response_body = get_current_time(tz_name)
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]

    elif method == 'POST' and path == '/api/v1/convert':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            response_body = convert_time(data)
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [response_body.encode('utf-8')]
        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'error': str(e)}).encode('utf-8')]

    elif method == 'POST' and path == '/api/v1/datediff':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            response_body = date_diff(data)
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [response_body.encode('utf-8')]
        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'error': str(e)}).encode('utf-8')]

    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not Found']

def get_current_time(tz_name):

    if tz_name not in all_timezones:
        tz_name = 'GMT'
    tz = timezone(tz_name)
    current_time = datetime.now(tz)
    return f"<html><body><h1>Current time in {tz_name} is {current_time.strftime('%Y-%m-%d %H:%M:%S')}</h1></body></html>"

def convert_time(data):

    date_str = data.get('date')
    tz_name = data.get('tz')
    target_tz_name = data.get('target_tz')

    if tz_name not in all_timezones or target_tz_name not in all_timezones:
        raise ValueError("Invalid timezone")

    tz = timezone(tz_name)
    target_tz = timezone(target_tz_name)
    date_time = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
    date_time = tz.localize(date_time)
    target_date_time = date_time.astimezone(target_tz)
    return json.dumps({'converted_date': target_date_time.strftime('%Y-%m-%d %H:%M:%S')})

def date_diff(data):

    first_date_str = data.get('first_date')
    first_tz_name = data.get('first_tz')
    second_date_str = data.get('second_date')
    second_tz_name = data.get('second_tz')

    if first_tz_name not in all_timezones or second_tz_name not in all_timezones:
        raise ValueError("Invalid timezone")

    first_tz = timezone(first_tz_name)
    second_tz = timezone(second_tz_name)

    first_date_time = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')
    first_date_time = first_tz.localize(first_date_time)

    second_date_time = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d')
    second_date_time = second_tz.localize(second_date_time)

    diff_seconds = int((second_date_time - first_date_time).total_seconds())
    return json.dumps({'difference_seconds': diff_seconds})

if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
