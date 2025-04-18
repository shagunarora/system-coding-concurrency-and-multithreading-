"""
Note: Below is overly complicated solution, when it could have been done
using just locks and some simple variables.

Please check standard approach for easier solution but this also works.

Problem:

    - Follow-ups on standard reader writer problem:
        - Create a writer-priority reader writer lock.
            - ReaderWriterLock should prioritize writer thread. As soon as a writer
              thread tries to access resource lock, no other reader threads should be 
              allowed to read. (Current reader threads should be allowed to 
              finish work.)
        
    Solution:
        - resource = 0
        - resource_lock => Lock to acquire to update resource.
        - writer_available = False # flag to indicate if writer available.

        - Condition variable to notify writer_available()
        - Every reader thread will check if writer_available
            - If yes, then wait until writer done with the updates.
        
"""

import threading
import time

class WritePriorityReaderWriterLock:
    def __init__(self):
        self.resource_lock = threading.Lock()
        self.read_lock = threading.Lock()
        self.write_lock = threading.Lock()

        self.writer_available = threading.Condition(self.write_lock)
        self.writer_available_flag = False

        self.reader_count = 0
        self.resource = 0

    def write(self, value):
        with self.writer_available:
            self.writer_available_flag = True
            self.writer_available.notify_all()  # Wake waiting readers so they re-check the flag

        with self.resource_lock:
            print(f"[Write] Thread {threading.get_ident()} updating value to {value}")
            self.resource = value
            time.sleep(2)

        with self.writer_available:
            self.writer_available_flag = False
            self.writer_available.notify_all()

    def read(self):
        with self.read_lock:
            with self.writer_available:
                while self.writer_available_flag:
                    self.writer_available.wait()

            self.reader_count += 1
            if self.reader_count == 1:
                self.resource_lock.acquire()

        print(f"[Read] Thread {threading.get_ident()} reading value: {self.resource}")
        time.sleep(1)

        with self.read_lock:
            self.reader_count -= 1
            if self.reader_count == 0:
                self.resource_lock.release()
