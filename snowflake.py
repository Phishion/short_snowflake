import time
import logging
import threading

# FORK 自 https://github.com/tarzanjw/pysnowflake
# short snowflake 提供了 3 种生成模式：normal, short, radical
# 3 种模式支持的并发数相同，均为 4096 / ms，但是 normal 支持节点 1024 个，short 支持的节点仅 4 个，radical 为单节点
# 在 normal 模式下 dc 的合法区间为 0～3，worker 的合法区间为 0～255
# 在 short 模式下，dc 参数将不起实际作用，worker 的合法区间为 0～3
# 在 radical 模式下，dc 和 worker 参数都不起实际作用
# short 模式的生成长度将于十几年后涨到 17 位，radical 几十年后仍然为 16 位

EPOCH_TIMESTAMP = 1350281600000


class Generator(object):

    def __init__(self, generator_type, dc, worker):
        self.dc = dc
        self.worker = worker
        self.node_id = ((dc & 0x03) << 8) | (worker & 0xff)
        self.generator_type = generator_type
        self.last_timestamp = EPOCH_TIMESTAMP
        self.sequence = 0
        self.sequence_overload = 0
        self.errors = 0
        self.generated_ids = 0
        if self.generator_type == "short":
            self.node_id = worker & 0x03
        self.mutex = threading.Lock()  # 线程锁，用于保证在多线程下也能正确工作(多进程无效，需要依靠 worker id 隔离)

    def get_next_id(self, threading_lock=False):
        if threading_lock:
            self.mutex.acquire()
        curr_time = int(time.time() * 1000)
        if curr_time < self.last_timestamp:  # stop handling requests til we've caught back up
            self.errors += 1
            logging.warning('Clock went backwards!')
        if curr_time > self.last_timestamp:
            self.sequence = 0
            self.last_timestamp = curr_time
        self.sequence += 1

        if self.sequence > 4095:  # the sequence is overload, just wait to next sequence
            logging.warning('The sequence has been overload')
            self.sequence_overload += 1
            time.sleep(0.001)
            return self.get_next_id()
        if self.generator_type == "short":
            generated_id = ((curr_time - EPOCH_TIMESTAMP) << 14) | (self.node_id << 12) | self.sequence
        elif self.generator_type == "radical":
            generated_id = ((curr_time - EPOCH_TIMESTAMP) << 12) | self.sequence
        elif self.generator_type == "normal":
            generated_id = ((curr_time - EPOCH_TIMESTAMP) << 22) | (self.node_id << 12) | self.sequence
        else:
            print("error generator type.")
            raise Exception
        self.generated_ids += 1
        if threading_lock:
            self.mutex.release()
        return generated_id

    @property
    def stats(self):
        return {
            'dc': self.dc,
            'worker': self.worker,
            'node_id': self.node_id,
            'timestamp': int(time.time() * 1000),  # current timestamp for this worker
            'last_timestamp': self.last_timestamp,  # the last timestamp that generated ID on
            'sequence': self.sequence,  # the sequence number for last timestamp
            'sequence_overload': self.sequence_overload,  # the number of times that the sequence is overflow
            'errors': self.errors,  # the number of times that clock went backward
        }


# 启动示例
# 注意，并发雪花 ID 需要生成保证多线程下开启线程锁，多进程下保证 worker id 的进程间唯一
flake_generator = Generator(generator_type="normal", dc=0, worker=0)
print(flake_generator.get_next_id(threading_lock=False))
print(flake_generator.stats)
