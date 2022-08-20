import os
import time
import logging
from datetime import datetime
import schedule
import requests
import xml.etree.ElementTree as ET 
import httplib2
from  googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import telebot
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from table.models import Order


CENTR_BANK_RU_URL = 'https://www.cbr.ru/scripts/XML_daily.asp'
GOOGLE_CREDENTIALS = 'creds.json'
SPREAD_SHEET_ID = '1C4gRZeZ1C-fqDkUcjRzqbW5qvx_rZYlwj_FNrte3pGI'
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  
TELEGRAM_CHAT_ID = '-686901726'  # replace with the desired chat


def main():
    """This function logging debug and runs scripts according 
    to the set schedule."""
    
    logging.basicConfig(filename='log_scripts.txt', level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')
    logging.debug('_________This is a start log message.__________')
    
    # script execution schedule can be edited as desired, for example:   
    # schedule.every().day.at("10:30").do(sending_notification) 
    schedule.every(1).minutes.do(save_data_in_db)
    schedule.every(2).minutes.do(sending_notification)
    while True:
        schedule.run_pending()


def get_usd_rate():
    """This function receives data on the dollar exchange rate
    in rubles from the official website of the
    Central Bank of the Russian Federation"""
    
    response = requests.get(CENTR_BANK_RU_URL)
    exchange_rates = response.content.decode('windows-1252', 'ignore')
    exchange_rates_xml = ET.fromstring(exchange_rates)
    for currency in exchange_rates_xml:
        if currency.attrib == {'ID': 'R01235'}:
            usd_rate = currency[4].text.replace(',', '.')
            return usd_rate


def get_orders_table():  
    """This function gets the data from the document using
    the Google API made in Google Sheets"""
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        GOOGLE_CREDENTIALS,
        ['https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = build('sheets', 'v4', http=httpAuth)
    table_values = service.spreadsheets().values().get(
        spreadsheetId=SPREAD_SHEET_ID,
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
            except ValueError:
                print('Value Error. An incorrect value was passed.')
            except Exception:
                print(Exception)
     
                               
def sending_notification():
    """This function checks the delivery date in Google Sheets and if
    the deadline is violated, it sends a notification to Telegram"""
    
    orders_table = get_orders_table()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    now = datetime.now()
    count_notify_messages = 0  # Telegram API block more 20 messages in minute.
    for row in orders_table:
            try:
                if row:                
                    delivery_date = datetime.strptime(row[3], '%d.%m.%Y')
                    if delivery_date < now:
                        bot.send_message(TELEGRAM_CHAT_ID, 
                            f'Delivery time violated.   Delivery date indicated: {row[3]}.\
                            Order number: {row[1]}.')
                        count_notify_messages += 1
                        if count_notify_messages == 19:
                            count_notify_messages = 0
                            time.sleep(60)                           
            except ValueError:
                print('Value Error.An incorrect value was passed.From notify func')        
            except Exception:
                print(f'From telegram notify func', Exception)
         
                        
if __name__ == "__main__":
    main()
   

