import threading

def worker():
    print("worker:", threading.current_thread())
    return 

threads = []
for i in range(5):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

print("threading count", threading.active_count())
print(threads)
print(threads[0].__dict__)

for th in threads :
    th.join（）
