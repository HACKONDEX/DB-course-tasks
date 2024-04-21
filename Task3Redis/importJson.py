import json
import numpy as np
import redis
import sys

str_data = open('./JEOPARDY_QUESTIONS1.json', 'r').read()
json_data = json.load(open('./JEOPARDY_QUESTIONS1.json'))

# print(str_data)
# print(json_data)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# insert one long str
redis_client.set('str_data', str_data)

# insert list 
list_data = str_data.split(',')
BATCH_SIZE = 1000
for i in range(0, len(list_data), BATCH_SIZE):
    redis_client.rpush('list_data', *list_data[i : i + BATCH_SIZE])

# # insert set
set_data = {s for s in list_data}
redis_client.sadd('set_data', *set_data)


floats = np.linspace(-5000, 5000, 500000)
floats_data = {str(f) : f for f in floats}
redis_client.zadd('floats_data', floats_data)

# should print 4
print(redis_client.dbsize())

from time import time

start = time()
res = redis_client.append('str_data', 'NewSuffixOfSomeVeryLongStr')
finish = time()
print(f'append-time: {(finish - start) * 1000: .2f} ms')

start = time()
res = redis_client.strlen('str_data')
finish = time()
print(f'strlen-time: {(finish - start) * 1000: .2f} ms')

start = time()
res = redis_client.lpush('list_data', *list_data[:10000])
finish = time()
print(f'lpush-time: {(finish - start) * 1000: .2f} ms')

start = time()
res = redis_client.zrange('floats_data', 0, 50000)
finish = time()
print(f'zrange-time: {(finish - start) * 1000: .2f} ms')

start = time()
res = redis_client.sismember('set_data', 'HISTORY')
finish = time()
print(f'sismember-time: {(finish - start) * 1000: .2f} ms')



