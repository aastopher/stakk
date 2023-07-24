from queue import Queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from states import IPTracker
import sutools as su

class RequestAgent:
    def __init__(self, work_queue: Queue, endpoint: callable, threshold: int, state: IPTracker):
        self.work_queue = work_queue
        self.endpoint = endpoint
        self.threshold = threshold
        self.name = endpoint.__name__
        self.ip_tracker = state
        self.timings = {} 

    def queue_proxy(self, proxy):
        ip = proxy['ip']  
        if not self.ip_tracker.has_seen_ip(ip): 
            self.work_queue.put(proxy)
            self.ip_tracker.add_ip(ip)

    def queue_proxies(self, proxy_list):
        with ThreadPoolExecutor() as executor:
            executor.map(self.queue_proxy, proxy_list)

    def start(self, thread_event: threading.Event):
        su.log().start.info(f'Starting {self.__class__.__name__} {self.name}')
        while not thread_event.is_set():
            try:
                if self.get_queue_size() <= self.threshold:
                    su.log().start.info(f'{self.name}: Collecting proxies')
                    start_time = time.perf_counter()
                    proxy_list = self.endpoint()
                    self.timings[self.name] = time.perf_counter() - start_time

                    su.log().start.info(f'{self.name}: Queuing collected proxies')
                    start_time = time.perf_counter()
                    self.queue_proxies(proxy_list)
                    self.timings[f'{self.name}_queue_proxies'] = time.perf_counter() - start_time

                    su.log().start.info(f'{self.name}: Sleeping... (1)')
                    thread_event.wait(1)
                else:
                    su.log().start.info(f'{self.name}: Queue size - {self.get_queue_size()}')
                    su.log().start.info(f'{self.name}: Data peak - {self.peek_queue_contents(1)}')
                    su.log().start.info(f'{self.name}: Sleeping... (3)')
                    thread_event.wait(3)
                print(f"{self.name} Timings: {self.timings}")
            except Exception as e:
                su.log().start.error(e)

    def start_worker(self, thread_event: threading.Event):
        self.worker_thread = threading.Thread(name=f'{self.__class__.__name__}_{self.name}', target=self.start, args=(thread_event,))
        self.worker_thread.start()
        su.log().start.info(f'{self.__class__.__name__} {self.name} Started')

    def join(self):
        self.worker_thread.join()

    def get_queue_size(self) -> int:
        return self.work_queue.qsize()

    def peek_queue_contents(self, size: int) -> int:
        return list(self.work_queue.queue)[:size]

su.logger(loggers=['start'], filecap=3, stream=True)