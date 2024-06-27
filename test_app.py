import unittest
import json
from datetime import datetime
from wsgiref.util import setup_testing_defaults
from io import BytesIO
import main

class TestWSGIApp(unittest.TestCase):

    def test_get_current_time_gmt(self):
        environ = {}
        setup_testing_defaults(environ)
        environ['PATH_INFO'] = '/'
        environ['REQUEST_METHOD'] = 'GET'

        def start_response(status, headers):
            self.assertEqual(status, '200 OK')
            self.assertIn(('Content-Type', 'text/html'), headers)

        response = main.application(environ, start_response)
        self.assertIn(b'Current time in GMT', response[0])

    def test_convert_time(self):
        environ = {}
        setup_testing_defaults(environ)
        environ['PATH_INFO'] = '/api/v1/convert'
        environ['REQUEST_METHOD'] = 'POST'
        request_body = json.dumps({
            "date": "12.20.2021 22:21:05",
            "tz": "EST",
            "target_tz": "Europe/Moscow"
        })
        environ['CONTENT_LENGTH'] = str(len(request_body))
        environ['wsgi.input'] = BytesIO(request_body.encode('utf-8'))

        def start_response(status, headers):
            self.assertEqual(status, '200 OK')
            self.assertIn(('Content-Type', 'application/json'), headers)

        response = main.application(environ, start_response)
        response_data = json.loads(response[0])
        self.assertIn('converted_date', response_data)

    def test_date_diff(self):
        environ = {}
        setup_testing_defaults(environ)
        environ['PATH_INFO'] = '/api/v1/datediff'
        environ['REQUEST_METHOD'] = 'POST'
        request_body = json.dumps({
            "first_date": "12.06.2024 22:21:05",
            "first_tz": "EST",
            "second_date": "12:30pm 2024-02-01",
            "second_tz": "Europe/Moscow"
        })
        environ['CONTENT_LENGTH'] = str(len(request_body))
        environ['wsgi.input'] = BytesIO(request_body.encode('utf-8'))

        def start_response(status, headers):
            self.assertEqual(status, '200 OK')
            self.assertIn(('Content-Type', 'application/json'), headers)

        response = main.application(environ, start_response)
        response_data = json.loads(response[0])
        self.assertIn('difference_seconds', response_data)

if __name__ == '__main__':
    unittest.main()