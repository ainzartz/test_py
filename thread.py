from threading import Thread
from time import sleep
from time import time
from functools import wraps



def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        return_value = func(*args, **kwargs)
        message = "Executing {} took {:.03} seconds.".format(func.__name__,
                                                             time() - start)
        print(message)
        return return_value
    return wrapper 



def fib(n):
    return fib(n - 1) + fib(n - 2) if n > 1 else n
    

def print_hello():
    while True:
        print("{} - Hello world!".format(int(time())))
        sleep(3)

def read_and_process_input(n):
    while True:
        print('fib({}) = {}'.format(n, log_execution_time(fib(n))))


def main():
    # Second thread will print the hello message. Starting as a daemon means
    # the thread will not prevent the process from exiting.
    t = Thread(target=print_hello)
    t.daemon = True
    t.start()
    # Main thread will read and process input
    read_and_process_input(27)

if __name__ == '__main__':
    main()
