# Run this python file to fetch fields in a region and add plants to it using the PlantGenerationSimulator.
import requests
import argparse
import json
import queue
import threading
import time
from urllib.request import urlopen
from start_bcd_v2 import plant_trees
from api_methods import assert_api_token_empty, assert_base_url_empty

# The arguments required for executing the method
parser = argparse.ArgumentParser()
parser.add_argument('--api-token', default="", help='The token for the api.')
parser.add_argument('--base-url', default="", help='The url of the api.')
args = parser.parse_args()


class MultiThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print(f"Output \n ** Starting the thread - {self.name}")
        self.process_queue()
        print(f" ** Completed the thread - {self.name}")

    def process_queue(self):
        while True:
            try:
                value = my_queue.get(block=False)
            except queue.Empty:
                return
            else:
                print("Field processed by %s:%d" % (self.name, value))
                plant_trees(value, 0, base_url=args.base_url, api_token=args.api_token)
                time.sleep(2)

# assert if the api token is empty
assert_api_token_empty(args.api_token)

# assert if the base url is empty
assert_base_url_empty(args.base_url)

#fetch all fields in Siebeldingen and Geilweilerhof that has no planter runs
url = '{}field?api-token={}'.format(args.base_url, args.api_token)
print(url)

#invoke the url and store the response
response = urlopen(url)
# parse the response to json
fields = json.loads(response.read())
# filter based on region
input_values = [x["properties"].get("id") for x in fields if (x["properties"].get(
    "name") == "Siebeldingen" or x["properties"].get("name") == "Geilweilerhof") and len(x["planter_runs"]) == 0]
print(input_values)
exit(1)
# fill the queue
my_queue = queue.Queue()
for x in input_values:
    my_queue.put(x)

#set no of threads
threads = [MultiThread("Thread%i" % i) for i in range(5)]

# start threads
for thread in threads:
    thread.start()

# wait for all threads to terminate
print('Main waiting for threads...')
for thread in threads:
    thread.join()
