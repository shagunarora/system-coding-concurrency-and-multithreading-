"""
Design and implement a Single Queue inside a fixed-size memory buffer.

Approach:
    - Single queue can be implemented by treating buffer as circular buffer.
"""

class Queue:
    def __init__(self, size):
        self.size = size
        self.buffer = [None]*size
        self.head = 0
        self.tail = 0
        self.count = 0 
    
    def enqueue(self, value):
        if self.count == self.size:
            raise Exception("Queue is full. No space left")
        
        self.buffer[self.tail] = value
        self.tail = (self.tail + 1) % self.size
        self.count += 1

    def deque(self):
        if self.count == 0:
            raise Exception("Queue is empty. Nothing to remove.")
        
        self.buffer[self.head] = None
        self.head = (self.head + 1) % self.size
        self.count -= 1
