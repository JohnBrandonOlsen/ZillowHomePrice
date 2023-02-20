#Pull Zillow Zestimates for properties

import requests
import json
from configparser import ConfigParser
import pandas as pd
import time
from twilio.rest import Client

def grab_data(login):

    z_info = requests.get('https://api.bridgedataoutput.com/api/v2/zestimates_v2/zestimates?access_token=' + login['Bridge']['Server_Token'] + 
                            '&zpid.in=' + login['Zillow']['P2_pid'] + ', ' + login['Zillow']['P1_pid'])
    details = json.loads(z_info.text)

    zestimates = [details['bundle'][0]['zestimate'], details['bundle'][1]['zestimate']]
    addresses = [details['bundle'][0]['address'], details['bundle'][1]['address']]

    return zestimates, addresses

def update_spreadsheet(zestimates, addresses):
    dates = [time.ctime()]
    
    try:
        open('/path/to/filename.csv', 'r')

        df = pd.DataFrame({addresses[0]: [zestimates[0]], addresses[1]: [zestimates[1]]}, index=dates)

        with open('/path/to/filename.csv', 'a') as f:
            df.to_csv(f, header=False, index=dates)
    except Exception as e:
        print(e)

def compare_values():

    with open('/path/to/filename.csv', 'r') as f:
        df = pd.read_csv(f)
        previous_P1_price = int(df.iat[-2,1])
        new_P1_price = int(df.iat[-1,1])
        previous_P2_price = int(df.iat[-2,2])
        new_P2_price = int(df.iat[-1,2])

            
    if new_P1_price == previous_P1_price and new_P2_price == previous_P2_price:
        message = None

        return(message)

    message = ""

    if new_P1_price > previous_P1_price:
        message = message + 'Your zestimate on Property1 increased by ' + \
            str(round((100*((new_P1_price/previous_P1_price)-1)),2)) + '%' \
            ' from ' + str('$' + "{:,}".format(previous_P1_price)) + ' to ' + str('$'\
            +"{:,}".format(new_P1_price)) + '.\n\n'

    if new_P1_price < previous_P1_price:
        message = message + 'Your zestimate on Property1 fell by ' + \
            str(round((100*(1-(new_P1_price/previous_P1_price))),2)) + '%' \
            ' from ' + str('$' + "{:,}".format(previous_P1_price)) + ' to ' + str('$'\
            +"{:,}".format(new_P1_price)) + '.\n\n'

    if new_P2_price > previous_P2_price:
        message = message + 'Your zestimate on Property2 increased by ' + \
            str(round((100*((new_P2_price/previous_P2_price)-1)),2)) + '%' \
            ' from ' + str('$' + "{:,}".format(previous_P2_price)) + ' to ' + str('$'\
            +"{:,}".format(new_P2_price)) + '.\n\n'


    if new_P2_price < previous_P2_price:
        message = message + 'Your zestimate on Property2 fell by ' + \
            str(round((100*(1-(new_P2_price/previous_P2_price))),2)) + '%' \
            ' from ' + str('$' + "{:,}".format(previous_P2_price)) + ' to ' + str('$'\
            +"{:,}".format(new_P2_price)) + '.\n\n'


    return(message)

def send_notification(login, message):
    account_sid = login['Twilio']['TWILIO_ACCOUNT_SID']
    auth_token = login['Twilio']['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    client.messages.create(from_=login['Twilio']['TWILIO_PH_NUM'], body = message,\
        to=login['Twilio']['SENDING_PH_NUMS'])

def main():
    
    login = ConfigParser()
    login.read('/path/to/filename.config')

    zestimates, addresses = grab_data(login)

    update_spreadsheet(zestimates, addresses)
    
    message = compare_values()

    if message != None:
        send_notification(login, message)

if __name__ == '__main__':
    main()
