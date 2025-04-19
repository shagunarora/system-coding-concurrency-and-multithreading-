"""
Context:
You're simulating a scientific experiment with 4 worker threads. The experiment runs in 3 phases, and in each phase:
    - All 4 workers must do some processing.
    - Once all workers finish the phase, they must synchronize at a barrier.
    - After phase 2, there's a chance that a global condition (like an emergency stop) might occur. This is signaled using an Event.
      If the event is set, all workers should stop further processing, even if they reached the barrier for phase 3.

Requirements:
    - Use a Barrier to ensure that all threads sync after each phase.
    - After Phase 2, randomly decide whether to set a stop Event.
    - In Phase 3, threads should check the Event before doing any work.
        - If the event is set, they should exit early.

    - Log each thread's behavior clearly — phase number, barrier wait, and whether they exited due to the event.

Approach: 
    - Three Phases:
        - phase_1_processing
        - phase_2..
        - phase_3..
    
    - 4 workers
    - Sync at end of each phase
        - Barrier waiting at end of each phase to ensure all 4 workers completed before moving to next phase.
          (Assuming wait after phase 3 also before exiting from main thread.)
        
    - After Phase_2, program randomly sets event: EMERGENCY_STOP. If event step, no more processing in phase 3.
        - Otherwise all 4 workers will start phase 3 processing. 
"""
import threading
import time
import random

class EarlyStopSimulation:
    def __init__(self):
        self.num_workers = 4
        self.barrier = threading.Barrier(self.num_workers)
        self.emergency_stop_event = threading.Event()

    def phase(self, phase_number):
        thread_id = threading.get_ident()
        print(f"[Thread-{thread_id}] in Phase {phase_number}")
        time.sleep(random.uniform(0.5, 1.0))

    def run(self):
        thread_id = threading.get_ident()
        print(f"[Thread-{thread_id}] Starting simulation")

        # Phase 1
        self.phase(1)
        self.barrier.wait()

        # Phase 2
        self.phase(2)
        index = self.barrier.wait()

        # Only the "leader" thread decides about emergency stop
        if index == 0:
            if random.choice([True, False]):
                print(f"[Thread-{thread_id}] EMERGENCY stop triggered!")
                self.emergency_stop_event.set()
            else:
                print(f"[Thread-{thread_id}] No emergency. Proceed to Phase 3.")

        # Phase 3
        if self.emergency_stop_event.is_set():
            print(f"[Thread-{thread_id}] Exiting early due to emergency.")
        else:
            self.phase(3)
            self.barrier.wait()

        print(f"[Thread-{thread_id}] Simulation done.")

# Start the simulation
simulation = EarlyStopSimulation()
threads = [threading.Thread(target=simulation.run) for _ in range(4)]

for t in threads:
    t.start()

for t in threads:
    t.join()