"""
Problem Statement:

1. One or more producers: threads that generate data and put it into a buffer.
2. One or more consumers: threads that take data from the buffer and process it.

Note: The buffer has limited capacity — it can only hold N items at a time. This is the "bounded" part.

Solution:
    1. Create a buffer and define is max_capacity.
    2. There will be multiple threads representing producers and same way multiple threads 
       representing consumers.
    3. Producers should only be able to insert if buffer not full:
        a. Use condition variable is_full to sync between consumers and producers.
    4. Similarly, use is_empty for consumers to notify consumers when buffer not empty.
    5. Both is_empty and is_full condition variable will be associated with the same lock as
       both consumers and producers trying to access same buffer.

Queries: Check concept what happens if I try acquire lock directly instead of cv, what all extra handling
  I will have to do ?

  : How can I add timeout when there is rate imbalance in producer consumer production and consumption
    rate.
"""
from threading import Condition, Lock, Thread, get_ident
import time

class BoundedBuffer:
    def __init__(self, max_capacity=1):
        self.buffer = []
        self.max_capacity = max_capacity
        self.buffer_lock = Lock()
        self.is_full = Condition(self.buffer_lock)
        self.is_empty = Condition(self.buffer_lock)
    
    def produce(self, item, producer_id):
        with self.is_full:
            while len(self.buffer) == self.max_capacity:
                print("Waiting as buffer full.")
                self.is_full.wait()
            
            print(f"Producer with id: {producer_id} adding element in buffer")
            self.buffer.append(item)
            self.is_empty.notify()
        
    def consume(self, consumer_id):
        with self.is_empty:
            while len(self.buffer) == 0:
                print("Waiting as buffer empty")
                self.is_empty.wait()
            
            print(f"Consumer with consumer_id: {consumer_id} will be consuming an item from bufer")
            self.buffer.pop()
            self.is_full.notify()


# Testing
bf = BoundedBuffer()

def produce():
    for i in range(2):
        bf.produce(i, get_ident())
        print(f"After producing {i},  Buffer state: ", bf.buffer)
        time.sleep(2)

def consume():
    for i in range(1):
        bf.consume(get_ident())
        print("Buffer state after consuming: ", bf.buffer)

# Create 2 producer and consumer threads each for testing
producers = [Thread(target=produce) for _ in range(2)]
consumers = [Thread(target=consume) for _ in range(2)]

for t in producers + consumers:
    t.start()

for t in producers + consumers:
    t.join()
