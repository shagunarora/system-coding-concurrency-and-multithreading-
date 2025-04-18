"""
You are designing a system that is shared by multiple threads, 
some of which perform read operations and others perform write 
operations. The goal is to synchronize access such that:

Rules:
1. Multiple readers can access the shared resource simultaneously.
2. Writers require exclusive access — no other readers or writers 
   can access the resource during a write.
3. No data inconsistency should occur due to concurrent access.
4. Avoid starvation:
    a. Optionally, try to ensure writer starvation doesn't happen 
       (some implementations prefer readers, others writers).


Implement the reader-writer logic using threading in Python (or any language), such that:
1. read() method can be called by multiple threads concurrently if no writer is active.
2. write() method must be called by one thread at a time, and only when no readers or 
   writers are active.

Approach:
    - reader_count = 0
    - resource_lock ==> This should be acquired by the first reader to block any writer
                        to perform write. This lock will be released by last reader before
                        leaving read block.
    - reader_lock = Used to update reader_count 

"""
import threading
import time

class ReaderWriterLock:
    def __init__(self):
        self.reader_count = 0
        self.lock = threading.Lock()
        self.resource_lock = threading.Lock()
        self.resource = 0

    def read(self):
        with self.lock:
            self.reader_count += 1
            if self.reader_count == 1:
                # Acquire resource_lock as well to make sure writer doesn't have 
                # permission to write to resource
                self.resource_lock.acquire()
            
        # Perform read
        print(f"[Read] ThreadID: {threading.get_ident()}, resource value: {self.resource}")
        time.sleep(1)

        with self.lock:
            self.reader_count -= 1
            if self.reader_count == 0:
                # No more readers then release resource lock.
                self.resource_lock.release()
    
    def write(self, value):
        with self.resource_lock:
            # Perform write
            print("Writing data to new value: ", value)
            self.resource = value
            time.sleep(2)

###### TESTING #########
rw_lock = ReaderWriterLock()

for _ in range(5):
    readers = [threading.Thread(target=rw_lock.read) for _ in range(4)]
    writers = [threading.Thread(target=rw_lock.write, args=(i,)) for i in range(1, 3)]

    for t in writers + readers:
        t.start()

    for t in  writers + readers:
        t.join()
