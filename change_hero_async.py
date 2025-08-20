import os
import time
import logging
from logging.handlers import RotatingFileHandler
import base64
import asyncio
import chardet


class HeroData:
    """英雄数据处理类"""

    def __init__(self, hero_dir='heroes', hero_encode_dir='heroes_encode', hero_decode_dir='heroes_decode'):
        self.start_time = time.time()  # 开始时间
        self.init_logging(self.ts(self.start_time))  # 初始化日志
        logging.info(f"开始时间：{self.data_ts(self.start_time)}")  # 打印开始时间
        self.end_time = time.time()
        self.hero_dir = hero_dir
        self.hero_encode_dir = hero_encode_dir
        self.hero_decode_dir = hero_decode_dir

    def encode_hero_data(self):
        try:
            self.check_dir(self.hero_encode_dir)  # 检查heroes_encode目录是否存在，如果不存在则创建
            # 收集所有文件
            files = []
            for filename in os.listdir(self.hero_dir):  # 遍历目录下的所有文件
                files.append(filename)
            asyncio.run(self.process_files_async(files, self.encode_single_file))  # 使用异步方式处理所有文件
        except KeyboardInterrupt:
            logging.warning("操作被用户中断")
        except Exception as e:
            logging.error(f"处理文件过程中发生错误：{e}")
        finally:
            self.get_runtime()  # 计算运行时间

    def decode_hero_data(self):
        try:
            self.check_dir(self.hero_decode_dir)  # 检查heroes_encode目录是否存在，如果不存在则创建
            # 收集所有文件
            files = []
            for filename in os.listdir(self.hero_encode_dir):  # 遍历目录下的所有文件
                files.append(filename)
            asyncio.run(self.process_files_async(files, self.decode_single_file))  # 使用异步方式处理所有文件
        except KeyboardInterrupt:
            logging.warning("操作被用户中断")
        except Exception as e:
            logging.error(f"处理文件过程中发生错误：{e}")
        finally:
            self.get_runtime()  # 计算运行时间

    @staticmethod
    async def process_files_async(filenames, callback):
        """异步处理所有文件"""
        logging.info(f"异步回调函数开始，文件名：{callback.__name__}.")
        tasks = []
        for filename in filenames:
            logging.info(f"正在读取文件：{filename}...")
            task = asyncio.create_task(callback(filename))  # 创建一个任务, 并返回一个 Task 对象
            tasks.append(task)
        # 任务的执行实际上是在 await asyncio.gather(*tasks) 这一行发生的。这行代码会并发执行所有之前创建的任务，并等待它们全部完成
        # 这种异步处理方式比同步方式快得多，因为它可以同时处理多个文件，而不是一个接一个地处理
        await asyncio.gather(*tasks)  # 执行并等待所有任务完成

    async def encode_single_file(self, old_filename):
        old_path = os.path.join(self.hero_dir, old_filename)  # 旧文件路径
        with open(old_path, 'r', encoding='utf-8') as f:
            old_content = f.read()  # 旧内容
        new_content = await self.callback_async(old_filename, old_content, self.encode_func_async)  # 新内容
        new_filename = old_filename.replace('.txt', '_encode.txt')  # 新文件名
        new_path = os.path.join(self.hero_encode_dir, new_filename)  # 新文件路径
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(new_content)  # 写入新内容
            logging.info(f"文件写入完毕：{new_filename}")

    async def decode_single_file(self, old_filename):
        old_path = os.path.join(self.hero_encode_dir, old_filename)  # 旧文件路径
        with open(old_path, 'r', encoding='utf-8') as f:
            old_content = f.read()  # 旧内容
        new_content = await self.callback_async(old_filename, old_content, self.decode_func_async)  # 新内容
        new_filename = old_filename.replace('_encode.txt', '_decode.txt')  # 新文件名
        new_path = os.path.join(self.hero_decode_dir, new_filename)  # 新文件路径
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(new_content)  # 写入新内容
            logging.info(f"文件写入完毕：{new_filename}")

    @staticmethod
    async def callback_async(old_filename, file_content, callback):  # 异步数据处理
        logging.info(f"数据处理开始：{old_filename}")
        processed = await callback(file_content)  # 回调函数(处理数据)
        logging.info(f"数据处理完毕：{old_filename}")
        return processed

    @classmethod
    async def encode_func_async(cls, file_content):  # 异步回调函数
        base64_str = cls.base64_encode(file_content)  # 进行Base64编码
        custom_str = cls.custom_encode(base64_str)  # 进行自定义加密
        await asyncio.sleep(3)  # 模拟处理数据耗时（异步版本）
        return custom_str  # 返回处理后的数据

    @classmethod
    async def decode_func_async(cls, custom_str):  # 异步回调函数
        base64_str = cls.custom_decode(custom_str) # 进行自定义解密
        decode_str = cls.base64_decode(base64_str) # 进行Base64解码
        await asyncio.sleep(3)  # 模拟处理数据耗时（异步版本）
        return decode_str  # 返回处理后的数据

    @staticmethod
    def base64_encode(string):
        byte_data = string.encode('utf-8')  # 先将字符串转换为字节（使用utf-8编码）
        base64_encoded = base64.b64encode(byte_data)  # # 进行Base64编码
        encode_str = base64_encoded.decode('utf-8')  # 将字节转换为字符串（使用utf-8解码）
        return encode_str

    @staticmethod
    def base64_decode(decode_str):
        byte_data = decode_str.encode('utf-8')  # 先将字符串转换为字节（使用utf-8编码）
        base64_decoded = base64.b64decode(byte_data)  # 进行Base64解码
        decode_str = base64_decoded.decode('utf-8')  # 将字节转换为字符串（使用utf-8解码）
        return decode_str

    @staticmethod
    def custom_encode(string):
        return "x" + string

    @staticmethod
    def custom_decode(string):
        return string[1:]

    def get_runtime(self):
        self.end_time = time.time()
        logging.info(f"结束时间：{self.data_ts(self.end_time)}")
        logging.info(f"总耗时：{self.end_time - self.start_time:.2f}秒")

    @staticmethod
    def data_ts(stime):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stime))

    @staticmethod
    def ts(stime):
        return time.strftime("%Y%m%d_%H%M%S", time.localtime(stime))

    @staticmethod
    def init_logging(ts):
        """初始化日志"""
        # 创建log目录（如果不存在）
        if not os.path.exists('log'):
            os.makedirs('log')
        # 创建logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # 设置日志级别为INFO
        # 创建文件处理器，使用轮转日志文件 (轮转日志文件是指当日志文件达到一定大小或满足某些条件时，系统会自动创建新的日志文件，并将旧的日志文件进行归档或删除的机制)
        file_handler = RotatingFileHandler(
            f'log/hero_data_{ts}.log',  # 主日志文件名：log/hero_data.log
            maxBytes=1024 * 1024,  # 日志文件大小限制为1MB
            backupCount=100  # 最多保留100个备份文件
        )
        file_handler.setLevel(logging.INFO)  # 设置日志级别为INFO
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)  # 将格式化器添加到处理器
        console_handler.setFormatter(formatter)  # 将格式化器添加到处理器
        # 添加处理器到logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    @staticmethod
    def check_dir(dir_name):
        if not os.path.exists(dir_name):  # 判断目录是否存在
            os.mkdir(dir_name)  # 创建目录
            logging.info(f"{dir_name} 目录创建完毕！")
        else:
            logging.info(f"{dir_name} 目录已存在！")


if __name__ == '__main__':
    hd = HeroData()
    hd.encode_hero_data()
    hd.decode_hero_data()