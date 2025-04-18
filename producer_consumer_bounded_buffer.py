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

Queries: 
    1. Check concept what happens if I try acquire lock directly instead of cv, what all extra handling
       I will have to do ?

       Solution: 
        - is_full internally is associated with self.buffer_lock (check code below using the same variables as mentioned below.)
        - If we do, [with is_full:], this basically acquires buffer_lock and when we come out of the context manager we release the 
          same buffer_lock. Check __enter__ and __exit__ defined in condition varaible definition, you will see they are internally 
          calling self.lock.__enter__() and self.lock.__exit__()
        
        - So basically, instead of with.is_full if I write with.buffer_lock, then that will work absolutely fine. But you should
          ensure you are using same lock which is associated with the condition variable.
        
        - Now, what will happen with below code:
            with self.buffer_lock:
                while len(self.buffer) == self.max_capacity:
                    print("Waiting as buffer full")
                    self.is_full.wait() --> This will release the lock.

            - Always think it as a thread T1, first acquired the lock using [with.buffer_lock] and then same thread checked for
              condition, if it has to wait, then same thread released the lock.
        
        - Conclusion: This will work absolutely fine, but you need to be careful you are using same lock. That is the reason 
                      its better to use with.is_full (No need to worry about locks)

        - Original code from BoundedBuffer class created below.

            def produce(self, item, producer_id):
                with self.is_full:
                    while len(self.buffer) == self.max_capacity:
                        print("Waiting as buffer full.")
                        self.is_full.wait()
                    
                    print(f"Producer with id: {producer_id} adding element in buffer")
                    self.buffer.append(item)
                    self.is_empty.notify()

    2. How can I add timeout when there is rate imbalance in producer consumer production and consumption
       rate.

       Solution: Lets say if there is no more consumer and you want producer to only wait for 5 seconds, 
                 if buffer still full i.e. no more consumer available, then return error.

                 Unable to produce as buffer full. Retry again.
                
                 def produce(self, item, producer_id):
                    with self.is_full:
                        start_time = time.time()
                        while len(buffer) == self.MAX_CAPACITY:
                            remaining_time = 5 - (time.time()-start_time)
                            if remaining_time == 0:
                                raise Exception("Unable to add item in buffer as buffer is full from last 5 seconds")
                            self.is_full.wait(timeout=remaining_time)
                        
                        buffer.append(item)
                        self.is_empty.notify()
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
            start_time = time.time()
            while len(self.buffer) == self.max_capacity:
                # Only wait until remaining_time is non_zero
                remaining_time = 5 - (time.time()-start_time)
                if remaining_time <= 0:
                    raise Exception("Unable to add item in buffer as buffer is full from last 5 seconds")
                
                print("Waiting as buffer full.")
                self.is_full.wait(timeout=remaining_time)
            
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
