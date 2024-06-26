## Task 3 practice with Redis

Install redis on MacOS
- `brew install redis`

Look at current status using brew service command
- `brew services info redis`

![plot](./screenshots/source1.png)

Run redis and check new status
- `brew services start redis`
- `brew services info redis`

![plot](./screenshots/source2.png)

Stop redis service
- `brew services stop redis`

In order to install RedisJson module do next steps
- `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh` - install rustc compiler with cargo build tool

Close current shell and open new session in order to reaload available paths from PATH var
- `git clone https://github.com/RedisJSON/RedisJSON.git`
- `cd RedisJSON`
- `cargo build --release && cargo test`

Reload shell and start redis server in directory RedisJSON
`redis-server --loadmodule ./target/release/librejson.dylib`

In other shell window open redis client
`redis-cli`

In redis client shell run to ensure RedisJSON module running
`info modules`

![plot](./screenshots/source3.png)

Install redis package for python3
`pip3 install redis --break-system-packages`

We can check DB size using DBSIZE command in redis-client

Then we can run python scriot, store some data in DB
We will use the json file from Mongo hometask

```
import json
import numpy as np
import redis
import sys

str_data = open('./JEOPARDY_QUESTIONS1.json', 'r').read()
json_data = json.load(open('./JEOPARDY_QUESTIONS1.json'))

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# insert one big str
redis_client.set('str_data', str_data)

# insert list 
list_data = str_data.split(',')
BATCH_SIZE = 1000
for i in range(0, len(list_data), BATCH_SIZE):
    redis_client.rpush('list_data', *list_data[i : i + BATCH_SIZE])

# insert set
set_data = {s for s in list_data}
# redis_client.sadd('set_data', *set_data)


floats = np.linspace(-5000, 5000, 500000)
floats_data = {str(f) : f for f in floats}
redis_client.zadd('floats_data', floats_data)

# should print 4
print(redis_client.dbsize())
```

Run `DBSIZE` in redis-client
![plot](./screenshots/source4.png)

Now run another script, to check some operations execution time

```
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
```
![plot](./screenshots/source5.png)

#### Conclusion

- All operations executed very fast if we compare with Postgres or Mongo. It is expected as Redis is an in-memory database. The advantage of storing data in memory(not disk) is that the representation of complex data structures is simpler tham om disk and it is easier to process them.

### Now let's set up redis cluster on 3 nodes

Create file __redis.conf__ with next content
```
port 8000
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes
```

- __cluster-enabled yes__ - tells redis that cluster configuration is enabled
- __cluster-config-file nodes.conf__ - standart configuration file for clustering
- __cluster-node-timeout__ - 5000 ms until node is considered to be failed
- __appendonly yes__ - enter data to this node

Then we create 3 directories with names __8000, 8001, 8002__ and copy the reids.confg file to each directory. Then in each configurational file change port number matching to the directory name. Run redis-server in each directory using 3 shell windows using command

- `redis-server ./redis.conf`

We can observe such output

![plot](./screenshots/source6.png)

Next we need to connect that nodes in one cluster. Run next command in new shell window

`redis-cli --cluster create 127.0.0.1:8000 127.0.0.1:8001 127.0.0.1:8002 --cluster-replicas 0`

The option __cluster-repicas 1__ means that for every node will be primary(master).

After running command above, we check the configuration in the output and type `yes`

![plot](./screenshots/source7.png)

Connect to one of the nodes using

- `redis-cli -p 8000 -c` Then use `CLUSTER SLOTS` and `CLUSTER INFO` to get information about cluster

![plot](./screenshots/source8.png)

Now we need to store some data in our cluster, but we __CAN't__ use our redis python client for such operations.
In order interact correctly install `redis-py-cluster` package for python, it also needs `setuptools` package

- `pip3 install redis-py-cluster --break-system-packages`
- `pip3 install setuptools --break-system-packages`

Store data in cluster such python script
```
from rediscluster import RedisCluster

startup_nodes = [
    {'host': '127.0.0.1', 'port': '8000'},
    {'host': '127.0.0.1', 'port': '8001'},
    {'host': '127.0.0.1', 'port': '8002'},
]

redis_cluster_client = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

str_data = open('./JEOPARDY_QUESTIONS1.json', 'r').read()

redis_cluster_client.set('key1', str_data)

import numpy as np

floats = np.linspace(-5000, 5000, 500000)
floats_data = {str(f) : f for f in floats}
redis_cluster_client.zadd('key2', floats_data)
```

Connect to some nodes and check keys they store - `redis-cli -p 8000 -c` - `keys "*"`

![plot](./screenshots/source9.png)

Now we change in configuration file `cluster-node-timeout`  to __5__ms for two nodes and restart the cluster
Then we insert a lot of data (nearly 50kk floats) and monitor the servers ouput

As we see on screenshots we got cluster Fail because of long reaceiving heatbeat from cluster `cc775294435d6f15389a7d8919872354446a37b3`
Then we see that the node became reachable again and the state was successfully recovered to __OK__

![plot](./screenshots/source10.png)
![plot](./screenshots/source11.png)

#### Conclusion

So we understand that in using redis-cluster across three nodes, the configuration of timeouts plays a crucial role in ensuring the system's reliability, performance, and overall fault tolerance.
