"""
Problem Statement:
    - You are building a JobScheduler where:
        - Some jobs depend on other jobs.
        - A job can only run when all its dependencies are completed.

    - We need to expose a function:
        - get_next_jobs_to_run(all_finished_jobs: set) →
        - Returns list of jobs whose dependencies are now satisfied and can be scheduled.

    - You must spawn a new thread for each job execution.
    - You must use locks when accessing shared data like job status.

Approach:
    - Create a JobScheduler class which will keep in looking in queue of available jobs to run the job.
    - After completion of any job, get all next eligible jobs and add it to queue.
"""
import threading
from collections import defaultdict

class JobScheduler:
    def __init__(self):
        self.dependency_graph = defaultdict(set)  # job -> jobs it depends on
        self.jobs = set()                         # all jobs
        self.finished_jobs = set()                # jobs completed
        self.lock = threading.Lock()              # lock for finished_jobs

    def add_job(self, job_name, depends_on=None):
        depends_on = depends_on or []
        self.jobs.add(job_name)
        for dep in depends_on:
            self.dependency_graph[job_name].add(dep)
            self.jobs.add(dep)

    def get_next_jobs_to_run(self):
        with self.lock:
            ready_jobs = []
            for job in self.jobs:
                if job not in self.finished_jobs:
                    if all(dep in self.finished_jobs for dep in self.dependency_graph[job]):
                        ready_jobs.append(job)
            return ready_jobs

    def mark_job_finished(self, job_name):
        with self.lock:
            self.finished_jobs.add(job_name)

    def run_job(self, job_name):
        # Simulate job execution
        print(f"Running job {job_name}...")
        threading.Event().wait(0.5)  # simulate some work
        print(f"Finished job {job_name}")
        self.mark_job_finished(job_name)

        # After finishing, check and run next available jobs
        self.schedule_ready_jobs()

    def schedule_ready_jobs(self):
        next_jobs = self.get_next_jobs_to_run()
        for job in next_jobs:
            thread = threading.Thread(target=self.run_job, args=(job,))
            thread.start()

    def start(self):
        self.schedule_ready_jobs()
