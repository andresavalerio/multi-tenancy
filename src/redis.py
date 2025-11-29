import redis
import logging

logger = logging.getLogger("app_logger")

redis_client: redis.Redis = None

def init_redis():
    global redis_client
    rpool = redis.ConnectionPool(host="localhost", port=6379, db=0)
    redis_client = redis.Redis(connection_pool=rpool, protocol=3)
    redis_client.config_set("maxmemory", "100mb")
    return redis_client

def close_redis():
    global redis_client
    redis_client.close()

def get_redis():
    return redis_client

def log_redis_info():
    info = redis_client.info()
    used_mem_h = info["used_memory_human"]
    total_mem_h = info["maxmemory_human"]
    used_mem = info["used_memory"]
    total_mem = info["maxmemory"]
    usage_rate = used_mem / total_mem
    logger.debug(
        f"Cache usage rate: {usage_rate*100:.2f}%, used: {used_mem_h}, total: {total_mem_h}"
    )
    hits = info["keyspace_hits"]
    misses = info["keyspace_misses"]
    mutations = info["keyspace_mutations"]
    rate = hits / (hits + misses)
    logger.debug(
        f"Cache hit rate: {rate*100:.2f}%, hits: {hits}, misses: {misses}, mutations: {mutations}"
    )