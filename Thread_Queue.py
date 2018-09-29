import threading
from queue import Queue
import time 

q = Queue() 
def worker():
    print("get Thread:",threading.current_thread())
    while True :
        item = q.get() 
        print("get Queue:",item)
        q.task_done()

def queue_put():
    print("Put thread:",threading.current_thread())
    for item in range(4):
        print("put queue:",item)
        q.put(item)

threads= []
for i in range(2):
    t = threading.Thread(target=worker)
    threads.append(t)

for i in range(2):
    t = threading.Thread(target=queue_put)
    threads.append(t)

print(threads)
for t in threads:
    t.start()
    if q.full() == True :
        print(t,q.queue)

q.join()

    