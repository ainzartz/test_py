import threading
print("threading count:",threading.active_count())

print("Main Thread:", threading.main_thread())

a= threading.enumerate() 

for i in a :
    print(i)
