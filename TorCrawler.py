import requests
import random
import csv
import string

proxiesDict = {
                "http": "http://localhost:9050",
                "https": "https://localhost:9050"
                }


ipTest = requests.get('http://httpbin.org/ip',proxies=proxiesDict)
print('Getting ip from httpbin... \n')
print(ipTest.text)
print(' is your ip seen through TOR. \n')

confirm = input('Is this correct? (y/n)')
if confirm.toLower() == 'y':
    print('Good')
elif confirm.toLower() == 'n':
    print('Make sure the tor service is running.')
    raise SystemExit
else:
    print('Enter y or n next time.')
    raise SystemExit

print('Testing relay with DuckDuckGo...')


with open('onions.csv', mode='w') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    while(True):
        randomStrings = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        peicesURL = {randomStrings, '.onion'}
        completeURL = ''.join(peicesURL)
        print(completeURL)
        r = requests.get(completeURL,proxies=proxiesDict)
        print(r.text)
        
