import threading
import time 
import logging 
import random 
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)

def n(i):
#    logging.debug("Starting my standard thread {}".format(i))
    logging.debug("Current Thread:{}".format(threading.current_thread()))
    #time.sleep(random.randint(1,50))
#    print("Total Number of active Threads-n: {}".format(threading.active_count()))
    time.sleep(random.randint(1,50))
    logging.debug("exiting {} ".format(i))
#    logging.debug("Exiting Current Thread:{}".format(threading.current_thread()))
def d():
    while True :
        logging.debug("Sending out Hertbit Signal, Current Thread:{}".format(threading.current_thread()))
        time.sleep(2)
        logging.debug("exiting Daemon")

print("Total Number of active Threads: {}".format(threading.active_count()))
d = threading.Thread(name='daemon', target=d)
d.daemon = True 
print("Start Daemon Thread")
d.start()
#d.join()

def main():
    print("Total Number of active Threads: {}".format(threading.active_count()))
#    j =  random.randint(2,50)
#    print ("Randon J is {}".format(j))

    for i in range(5):
        t = threading.Thread(name = 'none-daemon', target= n, args=(i,))
        t.start()
        print("Total Number of active Threads: {}".format(threading.active_count()))
        t.join()
#        print("Total Number of active Threads-join: {}".format(threading.active_count()))
        print("Thread Enumerating: {}".format(threading.enumerate()))
if __name__ == '__main__':
    main()   
    print("Total Number of active Threads-mainEnd: {}".format(threading.active_count()))
    print("Thread Enumerating: {}".format(threading.enumerate()))
 