import requests
import subprocess
import threading
from threading import Lock
import time
import queue
import re
import os
from stem import Signal
from stem.control import Controller


DELAY_BETWEEN_PRINTS = 2 # seconds.
THREAD_SPAWN_DELAY = 1 # second.
NUM_RESOLVERS = 20

num_resolvers_exited = 0



class TSCounter:

	def __init__(self, timeout=10):

		self.mutex = Lock()
		self.integer = 0
	
	def increment(self):

		with self.mutex:

			self.integer += 1
	
	def decrement(self):

		with self.mutex:

			self.integer -= 1
	
	def get(self):

		with self.mutex:

			return self.integer



class TSPrint:
	
	def __init__(self, timeout=10):

		self.mutex = Lock()
	

	def lock(self):

		self.mutex.acquire(blocking=True, timeout=10)
	

	def unlock(self):

		self.mutex.release()
	

	def print(self, text):

		with self.mutex:

			print(text)



class TSQueue:

	def __init__(self, timeout = 10):
		self.mutex = Lock()
		self.queue = []
		self.timeout = timeout

	def get(self):

		with self.mutex:

			if len(self.queue) != 0:

				element = self.queue.pop(0)

				return element
			
			else:
				
				return None
		
	
	def put(self, element):

		with self.mutex:

			self.queue.append(element)

			return True
	
	
	def qsize(self):

		with self.mutex:

			size = len(self.queue)

			return size
		
	
	def contains(self, element):

		with self.mutex:

			does_contain = True if (element in self.queue) else False

			return does_contain


	def __repr__(self):

		with self.mutex:

			string = str(self.queue)

			return repr(string)
		


# signal TOR for a new connection 
def renew_connection():
	with Controller.from_port(port = 9051) as controller:
		controller.authenticate(password=os.environ["TOR_CONTROL_PASSWORD"])
		controller.signal(Signal.NEWNYM)


def get_tor_session():
	session = requests.session()

	# Tor uses the 9050 port as the default socks port
	session.proxies = {
						'http':  'socks5h://127.0.0.1:9050',
						'https': 'socks5h://127.0.0.1:9050'
					  }

	return session


def extract_tor_addresses_from_text(text):
	# Tor addresses are random sequences of 16 of 56 characters followed by '.onion'
	search = re.findall("[0-9a-zA-Z]{56}\.onion", text)
	return search


def try_get_http_response(session, url):
	# Requests do not always go through. Especially on the deep web, there are a high number of inactive links.
	text = ""

	try:
		text = session.get(url).text
	except:
		text = ""

	return text




frontier_q = TSQueue(timeout = 10)
frontier_q.put('http://darkfailenbsdla5mal2mxn2uz66od5vtzd5qozslagrfzachha3f3id.onion')
frontier_q.put('http://answerszuvs3gg2l64e6hmnryudl5zgrmwm3vh65hzszdghblddvfiqd.onion')
frontier_q.put('http://g66ol3eb5ujdckzqqfmjsbpdjufmjd5nsgdipvxmsh7rckzlhywlzlqd.onion')
frontier_q.put('http://biblemeowimkh3utujmhm6oh2oeb3ubjw2lpgeq3lahrfr2l6ev6zgyd.onion')
frontier_q.put('http://vvedndyt433kopnhv6vejxnut54y5752vpxshjaqmj7ftwiu6quiv2ad.onion')
frontier_q.put('http://libraryfyuybp7oyidyya3ah5xvwgyx6weauoini7zyz555litmmumad.onion')

explored = TSQueue(timeout = 10)

ts_print = TSPrint()

num_resolvers_working = TSCounter()



def resolver_thread():
	global num_resolvers_working

	session = get_tor_session()

	ts_print.print("Resolver " + str(threading.get_ident()) + " spawned.")

	while True:

		url_to_explore = frontier_q.get()
		if url_to_explore == None:
			continue

		ts_print.print("Resolver " + str(threading.get_ident()) + " got url from frontier: " + url_to_explore + ".")
		num_resolvers_working.increment()

		# Don't re-explore a website.
		if not explored.contains(url_to_explore):

			website_text = try_get_http_response(session, url_to_explore)

			addresses_extracted = extract_tor_addresses_from_text(website_text)

			# Addresses may come without an http:// protocol at the beginning
			for i in range(len(addresses_extracted)):
				if not "http://" in addresses_extracted[i]:
					addresses_extracted[i] = "http://" + addresses_extracted[i]
			
			# Add found addresses to frontier_q
			for address in addresses_extracted:
				if not explored.contains(address) and not frontier_q.contains(address):
					frontier_q.put(address)

			if website_text != "":
				ts_print.print("Resolver " + str(threading.get_ident()) + " found new url: " + url_to_explore + ".")
				explored.put(url_to_explore)
		
		num_resolvers_working.decrement()
		time.sleep(0.25)


def main_thread():
	# Main thread will check the frontier queue and explored queue every 1 second.
	previous_frontier_length = frontier_q.qsize()
	previous_explored_length = explored.qsize()

	while True:

		new_frontier_length = frontier_q.qsize()
		new_explored_length = explored.qsize()

		if (previous_frontier_length != new_frontier_length) or (previous_explored_length != new_explored_length):

			# Lock all prints temporarily.
			ts_print.lock()
			subprocess.run(['clear'])
			print("Frontier: \n---------------------------------\n" + str(frontier_q) + "\n\n")
			print("Explored: \n---------------------------------\n" + str(explored) + "\n\n")
			print("Frontier Length: " + str(new_frontier_length))
			print("Explored Length: " + str(new_explored_length))
			print("Resolvers exited: " + str(num_resolvers_exited))
			print("Resolvers working: " + str(num_resolvers_working.get()))
			print("\n\n")
			print("Thread Actions: \n---------------------------------")
			ts_print.unlock()

			previous_frontier_length = new_frontier_length
			previous_explored_length = new_explored_length

		time.sleep(DELAY_BETWEEN_PRINTS)






if __name__ =="__main__":

	main_thread_handle = threading.Thread(target=main_thread, args=())
	resolvers = []

	for i in range(0, NUM_RESOLVERS):
		resolvers.append(threading.Thread(target=resolver_thread, args=()))

	# Start all threads, ending with the main thread.
	for resolver in resolvers:
		resolver.start()

	# Give time to see the threads spawn.
	time.sleep(THREAD_SPAWN_DELAY)
	
	main_thread_handle.start()

	resolvers_exited = {}
	while True:

		for resolver in resolvers:
			# For each resolver, if it has become un-alive but was previously alive, it just exited.
			if resolver.is_alive() == False\
					and resolver.ident in resolvers_exited.keys()\
					and resolvers_exited[resolver.ident] == False:

				resolvers_exited[resolver] = True
				num_resolvers_exited += 1
		
		if num_resolvers_exited == NUM_RESOLVERS:
			ts_print.print("All resolvers exited.")
			break
		
		time.sleep(0.5)


	ts_print.print("Frontier Queue is empty.")

	main_thread_handle.join()

