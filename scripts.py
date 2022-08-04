import os
import schedule
import requests
import xml.etree.ElementTree as ET 
import httplib2
from  googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from table.models import Order


def get_usd_rate():
    """This function receives data on the dollar exchange rate
    in rubles from the official website of the
    Central Bank of the Russian Federation"""
    
    URL = 'https://www.cbr.ru/scripts/XML_daily.asp'
    
    response = requests.get(URL)
    exchange_rates = response.content.decode('windows-1252', 'ignore')
    
    exchange_rates_xml = ET.fromstring(exchange_rates)
    for currency in exchange_rates_xml:
        if currency.attrib == {'ID': 'R01235'}:
            usd_rate = currency[4].text.replace(',', '.')
            return usd_rate


def get_orders_table():  
    """This function gets the data from the document using
    the Google API made in Google Sheets"""
         
    CREDENTIALS_FILE = 'creds.json'
    SPREADSHEET_ID = '1C4gRZeZ1C-fqDkUcjRzqbW5qvx_rZYlwj_FNrte3pGI'
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = build('sheets', 'v4', http=httpAuth)

    table_values = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='A2:500',
        majorDimension='ROWS'
    ).execute()
    return table_values['values']

def save_data_in_db():
    """This function saves data from google sheets in to 
    Postgres database"""
    
    usd_rate = get_usd_rate()
    orders_table = get_orders_table()
    for row in orders_table:
        if row:
            try:
                row[2] = int(row[2])
                temp_row = row[3].split('.')
                row[3] = '-'.join(temp_row[::-1])
                cost_in_rubles = row[2] * float(usd_rate)
                row.append(round(cost_in_rubles, 2))
                order = Order(field_number=row[0],
                              order_number=row[1],
                              cost_in_dollars=row[2], 
                              deliver_time=row[3],
                              cost_in_rubles=row[4])
                order.save()
            except Exception:
                print(Exception)
        
def main():
    """This function is scheduled to update the data in the
    Database every two minutes"""
    
    schedule.every(2).minutes.do(save_data_in_db)
    while True:
        schedule.run_pending()
    
if __name__ == "__main__":
    main()
   

