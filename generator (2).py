# def square_numbers(nums):
#     result = []
#     for i in nums:
#         result.append(i * i)
#     return result

# my_nums = square_numbers([1, 2, 3, 4, 5])

# print (my_nums)



# def square_numbers(nums):
#     for i in nums:
#        yield i * i

# my_nums = square_numbers([1, 2, 3, 4, 5])

# for num in my_nums:
#     print(num)


from __future__ import division
import os
import psutil
import random
import time

names = ['1', '2', '3', '4', '5', '6']
majors = ['A', 'B', 'C', 'D', 'E']

process = psutil.Process(os.getpid())
mem_before = process.memory_info().rss / 1024 / 1024


def people_list(num_people):
    result = []
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
for p in people:
     print(p)

print ('Before MEM: {} MB'.format(mem_before))
print ('After MEM: {} MB'.format(mem_after))
print ('Total Sec: {:.6f} sec'.format(total_time))