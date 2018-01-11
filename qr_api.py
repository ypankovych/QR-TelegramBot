import re
import os
import pyqrcode
import urllib.request

import requests

pattern = re.compile(r'Данные:\s(.*)<br')
read_code = 'https://decodeit.ru/index-ajax.php'

def create_qr(text, user_id):
    file_name = f'{user_id}.png'
    try:
        qr = pyqrcode.create(text)
    except UnicodeEncodeError:
        return {'status': 0,'message': 'Error. This encoding is not supported.'}
    qr.png(file_name, scale=5)
    try:
        return open(file_name, 'rb').read()
    finally:
        os.remove(file_name)

def read_qr(qr_code):
    files = {'value': ('filename', qr_code)}
    data = {'act': 'qr_decode'}
    response = requests.post(read_code,  data=data, files=files, timeout=1000).json()
    qr_data = pattern.search(response['html'])
    if qr_data:
        return {'status': 1,'result': qr_data.group(1)}
    return {'status': 0, 'message': 'Error. Data not found.'}
