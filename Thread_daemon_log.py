import threading
import time 
import logging 
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)

def n():
    logging.debug("Starting")
    logging.debug("exiting")

def d():
    logging.debug("Starting")
    time.sleep(5)
    logging.debug("exiting")

if __name__ == '__main__':
    t = threading.Thread(name = 'none-daemon', target= n)
    d = threading.Thread(name='daemon', target=d)
    d.daemon = True 

    d.start()
    t.start()
    d.join()
    t.join()
