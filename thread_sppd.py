import time
import threading

def countdown(n):
    start = time.time()
    print("countdown thread", threading.current_thread())
    while n > 0 :
        n -=1
        print("countdown thread", threading.current_thread()," -->", n)
    end = time.time()
    print("exec",float(end)-float(start))
    return n

count = 10
# countdown(count) # single thread
#Multi thread
t1 = threading.Thread(target=countdown, args=(count//2,))
t2 = threading.Thread(target=countdown, args=(count//2,))

t1.start()
t2.start()
t1.join()
t2.join()
