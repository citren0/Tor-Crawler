# Tor-Crawler
A simple Tor Crawler written in Python 3 packaged with a thread-safe counter and queue.

## Dependencies
You will need a running tor daemon proxy on your system.

## Run
If your current user doesn't have permission to interact with the tor service, you need to sudo to the tor user:\
  $ sudo -g tor python3 ./tor_crawler.py
If you have permission:\
  $ python3 ./tor_crawler.py
