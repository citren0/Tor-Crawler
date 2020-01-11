import requests
import random
import csv
import string
import time
import subprocess
import os
import socket
import socks
from stem import Signal
from stem.control import Controller


if not os.geteuid() == 0:
    exit("\nOnly root can run this script\n")



subprocess.run("cd && bash service tor restart", shell=True)

with Controller.from_port(port=9050) as controller:



    def connectTor():
        from GenTorHash import genTorPassHash
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
        socket.socket = socks.socksocket
    #-------------------------------------------------------------------


    def renew_tor():
        torHash = input("What tor password will you use?")
        torHash = genTorPassHash(torHash)
        controller.authenticate(torHash)
        controller.signal(Signal.NEWNYM)
        time.sleep(controller.get_newnym_wait())
    #-------------------------------------------------------------------


    def showip():
        ipTest = requests.Session()
        ipTestText = ipTest.get('http://httpbin.org/ip')
        print('Getting ip from httpbin... \n')
        print(ipTestText)
        print(' is your ip seen through TOR. \n')

        confirm = input('Is this correct? (y/n)')
        if confirm.lower() == 'y':
            print('Good')
        elif confirm.lower() == 'n':
            print('Make sure the tor service is running.')
            raise SystemExit
        else:
            print('Enter y or n next time.')
            raise SystemExit
    #-------------------------------------------------------------------


    #Connecting to tor for the first time.
    
    time.sleep(2)
    renew_tor()
    connectTor()


    with open('onions.csv', mode='w') as file:
        worked = False
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        while(True):
            randomStrings = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
            completeURL = "http://" + randomStrings.lower() + ".onion"
            print(completeURL)
            try:
                r = requests.get(completeURL, timeout=5)
                if r:
                    print("\n\n\n\n\n----URL VALID----", completeURL)
                    writer.writerow(['Valid: ', completeURL])
                    time.sleep(5)
            except Exception as e:
                print("URL invalid")
                print(e)
        
        
        
#"http://3g2upl4pq6kufc4m.onion/"
