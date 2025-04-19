"""
Problem:

You are to implement a system with:
    - Multiple producer threads
    - Multiple consumer threads
    - A fixed-size buffer that operates like a circular queue

Rules:
    - Producers:
        - Continuously generate data.
        - Must wait if the buffer is full.
        - Insert into the buffer when there is space.

    - Consumers:
        - Continuously consume data.
        - Must wait if the buffer is empty.
        - Remove from the buffer when there is data.
    - The buffer has a fixed size N and behaves in a circular manner:
        - When the buffer end is reached, wrap around to the start.
    - You must handle synchronization properly so:
        - No data is overwritten or missed
        - No race conditions
        - No deadlocks or starvation

Approach:
    - Queue: Fixed Buffer in form of circular queue.
    - next index = (index + 1) % BUFFER_SIZE (Access elements in circular order)
    - Consumers: 2 (continuosly consuming data if avaialble)
    - Producers: 2 (continuously streaming data if space exist)
    - Queue: Shared resource (Maintain lock to allow only one thread to access at a time.)


"""

import threading
import time
import random

class CircularBoundedBuffer:
    def __init__(self, capacity):
        self.size = capacity
        self.buffer = [None]*capacity
        self.lock = threading.Lock()
        self.consumer_index = 0
        self.producer_index = 0
        self.space_available = threading.Condition(self.lock)
        self.content_available = threading.Condition(self.lock)
    
    def produce(self, id):

        # For DEMO a producer will produce 5 times. (It could be a stream also in reality)
        for value in range(5):
            with self.space_available:
                while self.buffer[self.producer_index] != None:
                    self.space_available.wait()
                
                print(f"Producer with id: {id} producing content in buffer.")
                time.sleep(random.uniform(0.5, 1))
                self.buffer[self.producer_index] = value
                self.content_available.notify_all()

                # Check if next index free
                self.producer_index = (self.producer_index + 1)%self.size
            
    def consume(self, id):
        """
        Wait for 5 seconds for new content, if no new content then return.
        """
        while True:
            with self.content_available:
                start_time = time.time()
                while self.buffer[self.consumer_index] == None:
                    remaining_time = 5 - (time.time() - start_time)
                    if remaining_time <= 0:
                        print(f"No new content found. Consumer {id} waited for 5 seconds. Now returning.")
                        return
                    self.content_available.wait(timeout=remaining_time)
                
                print(f"Consumer with id: {id}, consuming buffer value: {self.buffer[self.consumer_index]}")
                self.buffer[self.consumer_index] = None
                self.space_available.notify_all()
                self.consumer_index = (self.consumer_index + 1) % self.size

##### TESTING #######
cbb = CircularBoundedBuffer(3)

producers = [threading.Thread(target=cbb.produce, args=(id,)) for id in range(1, 3)]
consumers = [threading.Thread(target=cbb.consume, args=(id,)) for id in range(1, 3)]

for t in producers + consumers:
    t.start()

for t in producers + consumers:
    t.join()