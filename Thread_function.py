import threading
print ("threading count:",threading.active_count())
print ("main thread:", threading.main_thread())
print ("Current Thread:",threading.current_thread())

#check whole thread in process 
threads = threading.enumerate()
for i in threads :
    print(i)
