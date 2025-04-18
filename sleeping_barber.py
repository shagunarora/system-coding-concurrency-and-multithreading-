"""
Problem Statement:
    You are modeling a barber shop with:
        - One barber (single worker thread)
        - A limited number of waiting chairs (say N)
        - Multiple customer threads arriving randomly

    Rules:
        - If no customers are present, the barber sleeps (waits).
        - If a customer arrives and the barber is sleeping, they wake him up.
        - If the barber is busy and there's a free chair, the customer waits.
        - If no chair is free, the customer leaves the shop.
        - Only one customer is served at a time.

    Objective:
        - Implement the synchronization logic so that:
        - Barber and customers coordinate properly
        - Waiting area capacity is respected
        - No race conditions or deadlocks occur

Solution:
    - States:
        - Barber
            - sleeping/waiting
            - busy
        
        - Customer
            - Being served.
            - Waiting on chair (If free chair available)
            - left


    - Customers Flow:
        - customer_counter_lock = Lock()
        - number_of_customers = 0
        - customer_available = Condition(customer_counter_lock)
        - max_limit 
        - if number_of_customers < max_limit:
            - acquire lock and update count of number_of_customers
            - notify barber # using some cv
        
    - Barber Flow
        - with customer_available:
            while number_of_customers == 0:
                customer_available.wait()
            
            number_of_customers -= 1
        
        - Perform processing (sleep - 2s)

"""
import threading
import time

class SleepingBarber:
    def __init__(self, N):
        self.customers_count = 0
        self.max_limit = N
        self.counter_lock = threading.Lock()
        self.customer_available = threading.Condition(self.counter_lock)
    
    def handle_customer(self):
        with self.customer_available:
            if self.customers_count == self.max_limit:
                print("No available waiting seat. Come back later.")
                return
            
            self.customers_count += 1
            self.customer_available.notify()
    
    def process_customers(self):
        while True:
            with self.customer_available:
                while self.customers_count == 0:
                    print("Barber sleeping...")
                    self.customer_available.wait()

                self.customers_count -= 1  # Just one customer per loop

            print("Barber is serving a customer...")
            time.sleep(2)
