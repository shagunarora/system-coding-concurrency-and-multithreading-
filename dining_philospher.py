"""
Problem Statement:

There are 5 philosophers sitting at a round table. Each philosopher does two things:
    - Think
    - Eat

Between each pair of philosophers is one fork, and a philosopher needs both left and right 
forks to eat. Philosophers must avoid deadlock (where everyone is holding one fork and waiting 
for another) and starvation (where one philosopher never gets to eat).


Note: There are 2 more approaches, will add those later.

Approach:

    - Problems here will be circular wait, if every philospher thread tries to pick fork in clockwise direction.
    - To break circular wait, schedule threads to pick fork based on ids assigned:
        - odd id threads can pick left fork 
        - even id threads should pick right fork.
    
    - A philospher thread should have access to left and right fork locks, that will be needed for eating.
    - Philospher object:
        - philoshper_id
        - left_lock
        - right_lock

"""
from threading import Lock, Thread
import time
import random

class Philospher(Thread):
    def __init__(self, id, left_fork: Lock, right_fork: Lock):
        super().__init__()  
        self.id = id
        self.left_fork = left_fork
        self.right_fork = right_fork
    
    def think(self):
        print(f"I am {self.id} thinking...")
        time.sleep(random.uniform(0.5,1))
    
    def eat(self):
        # Acquire lock based on order defined for even and odd phiosphers.
        first, second = (self.left_fork, self.right_fork) if self.id & 1 else (self.right_fork, self.left_fork)
        with first:
            with second:
                print(f"I am {self.id} eating..")
                time.sleep(random.uniform(1, 1.5))
    
    def run(self):
        for _ in range(3):
            self.think()
            self.eat()


# | 0 | 1 | 2 | 3 | 4 
forks = [Lock() for _ in range(5)]
philosphers = [Philospher(id, forks[id], forks[(id+1)%5]) for id in range(5)]

for philospher in philosphers:
    philospher.start()

for philospher in philosphers:
    philospher.join()    
