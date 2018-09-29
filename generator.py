from __future__ import division 
import psutil
import os
import random
import time 

names = [ 'david','john','kim','lee','park']
majors = ['computer','meath','bio','mis','english']
print(dir(psutil))

print('-'*30)
print(type(psutil))
print('-'*60)
process = psutil.Process(os.getpid())
print(type(process))
print(process)
print('-'*60)
print(dir(process))
mem_before = process.memory_info().rss /1024 / 1024
print(type(process.memory_info().rss))
print('-'*60)
print(dir(process.memory_info().rss))
print('-'*60)
print(process.memory_info().rss)
print('-'*60)
def people_list(num_people):
    result=[]
    for i in range(num_people):
        person = {
            'id': i,
            'name': random.choice(names),
            'major': random.choice(majors)
        }
        result.append(person)
    return result 

def people_generator(num_people):
    for i in range(num_people):
        person = {
            'id': i,
            'name': random.choice(names),
            'major': random.choice(majors)
        
        }
        yield person 
t1 = time.clock()
#people = people_list(1000000)
people = people_generator(1000000)
t2 = time.clock()
mem_after = process.memory_info().rss / 1024 / 1024
total_time = t2 - t1
print ('afeter Memory: {} MB'.format(mem_before))
print ('Before Memory: {} MB'.format(mem_after))
print ('total Time:{:.6f} sec'.format(total_time))

