import requests
import xml.etree.ElementTree as ET 
import httplib2
from  googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from table.models import Order
import schedule
import re



def send_request(url):
    response = requests.get(url)
    return response.content

def get_usd():
    url_cb = 'https://www.cbr.ru/scripts/XML_daily.asp'
    str_bytes = send_request(url_cb)
    str_python = str_bytes.decode('windows-1252', 'ignore')
    root = ET.fromstring(str_python)

    for child in root:
        if child.attrib == {'ID': 'R01235'}:
            usd_str = child[4].text
            curs_usd = usd_str.replace(',', '.')
            return curs_usd

def get_sheets():       
    CREDENTIALS_FILE = 'creds.json'
    spreadsheet_id = '1C4gRZeZ1C-fqDkUcjRzqbW5qvx_rZYlwj_FNrte3pGI'
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'])

    httpAuth = credentials.authorize(httplib2.Http())
    service = build('sheets', 'v4', http=httpAuth)

    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='A2:500',
        majorDimension='ROWS'
    ).execute()
    return values['values']

def save_data():
    usd_cost = get_usd()
    orders_table = get_sheets()
    for row in orders_table:
        if row:
            try:
                row[2] = int(row[2])
                temp_r = row[3].split('.')
                row[3] = '-'.join(temp_r[::-1])
                cost_rub = row[2] * float(usd_cost)
                row.append(round(cost_rub, 2))
                order = Order(field_number=row[0], order_number=row[1],
                            cost_in_dollars=row[2], deliver_time=row[3],
                            cost_in_rubles=row[4])
                order.save()
            except Exception:
                print(Exception)
        
def main():
    schedule.every(2).minutes.do(save_data)
    
    while True:
        schedule.run_pending()
    
if __name__ == "__main__":
    main()
   