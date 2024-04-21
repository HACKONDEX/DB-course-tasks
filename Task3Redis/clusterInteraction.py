from rediscluster import RedisCluster

startup_nodes = [
    {'host': '127.0.0.1', 'port': '8000'},
    {'host': '127.0.0.1', 'port': '8001'},
    {'host': '127.0.0.1', 'port': '8002'},
]

redis_cluster_client = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

str_data = open('./JEOPARDY_QUESTIONS1.json', 'r').read()

redis_cluster_client.set('key2', str_data)

import numpy as np

floats = np.linspace(-5000, 5000, 5000000)
floats_data = {str(f) : f for f in floats}
redis_cluster_client.zadd('key3', floats_data)
