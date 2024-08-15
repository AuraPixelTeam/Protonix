import threading
import queue
import time
import psutil
import logging

from .Worker import Worker


class WorkerManager:
    def __init__(self, max_threads=5, max_memory_usage=None, max_cpu_usage=None, retry_limit=3):
        self.max_threads = max_threads
        self.max_memory_usage = max_memory_usage
        self.max_cpu_usage = max_cpu_usage
        self.retry_limit = retry_limit
        self.tasks = queue.Queue()
        self.threads = []
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def worker(self):
        while not self.stop_event.is_set():
            try:
                item = self.tasks.get(timeout=1)
                if item is None:
                    break
                task, args, kwargs = item

                retry_count = 0
                while retry_count < self.retry_limit:
                    try:
                        while not self.check_resources() and not self.stop_event.is_set():
                            time.sleep(1)
                        if not self.stop_event.is_set():
                            task(*args, **kwargs)
                        break
                    except Exception as e:
                        logging.error(f"Error executing task: {e}")
                        retry_count += 1
                        if retry_count >= self.retry_limit:
                            logging.error(f"Task failed after {self.retry_limit} retries.")

                self.tasks.task_done()

            except queue.Empty:
                continue

    def add_task(self, task, *args, **kwargs):
        self.tasks.put((task, args, kwargs))

    def start_threads(self):
        for _ in range(self.max_threads):
            thread = Worker(target=self.worker)
            thread.start()
            self.threads.append(thread)

    def stop_threads(self):
        self.stop_event.set()
        for _ in range(self.max_threads):
            self.tasks.put(None)
        for thread in self.threads:
            thread.join()

    def wait_for_completion(self):
        self.tasks.join()
        self.stop_threads()

    def check_resources(self):
        if self.max_memory_usage and psutil.virtual_memory().percent > self.max_memory_usage:
            return False
        if self.max_cpu_usage and psutil.cpu_percent() > self.max_cpu_usage:
            return False
        return True
