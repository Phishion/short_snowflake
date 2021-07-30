import unittest
import snowflake
from multiprocessing.dummy import Pool as ThreadPool


class SnowFlakeIdGeneratorCase(unittest.TestCase):
    # 单线程测试
    def test_single_thread(self):
        flake_generator = snowflake.Generator(generator_type="normal", dc=0, worker=0)
        flake_list = []
        for value in range(10000):
            flake_id = flake_generator.get_next_id()
            flake_list.append(flake_id)
        self.assertEqual(len(flake_list), len(set(flake_list)))

    # 多线程加锁保证获取正确
    def test_muti_threads(self):
        flake_generator = snowflake.Generator(generator_type="normal", dc=0, worker=0)
        flake_list = []

        def append_flake_id(count):
            flake_id = flake_generator.get_next_id(threading_lock=True)
            flake_list.append(flake_id)

        pool = ThreadPool(1000)
        pool.map(append_flake_id, range(50000))
        pool.close()
        self.assertEqual(len(flake_list), len(set(flake_list)))
