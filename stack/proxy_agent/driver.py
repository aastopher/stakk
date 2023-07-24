import threading
from queue import Queue
from agents import RequestAgent
from states import IPTracker
from pipeline_funcs import (get_free_proxy_list, get_geo_list, get_pworld_list)

def start_agent():
    # Create queues
    config_queue = Queue()

    # Create a thread event
    thread_event = threading.Event()

    # Init function list
    functions = [get_free_proxy_list, get_geo_list, get_pworld_list]
    threshold = 100
    state = IPTracker()

    # Create a ConfigWorker for each function
    config_workers = [RequestAgent(config_queue, func, threshold, state) for func in functions]

    # Start the workers
    for worker in config_workers:
        worker.start_worker(thread_event)

    try:
        while True:
            # Main thread does nothing but wait for keyboard interrupt
            pass
    except KeyboardInterrupt:
        print("Stopping workers...")
        # Set the event to signal the workers to stop
        thread_event.set()
        # Wait for the workers to stop
        for worker in config_workers:
            worker.join()

if __name__ == "__main__":
    start_agent()