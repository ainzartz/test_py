from threading import Thread

def do_work(start, end, result):
    sum = 0 
    for i in range(start, end):
        sum += i 
    result.append(sum)
    return

if __name__ == "__main__":
    T_START, T_END = 0, 20000000
    print(type(T_START))
    print (T_START)
    result = list() 
    th1 = Thread(target=do_work, args=（T_START,　T_END, result))
#    th1.start()
#    th1.join()
#print( sum(result) )

