import os
import time
import logging
from logging.handlers import RotatingFileHandler
import base64
import asyncio


class HeroData:
    """英雄数据处理类"""

    def __init__(self):
        self.start_time = time.time()  # 开始时间
        self.init_logging(self.ts(self.start_time))  # 初始化日志
        logging.info(f"开始时间：{self.data_ts(self.start_time)}")  # 打印开始时间
        self.end_time = time.time()

    def change_hero_data(self):
        """遍历heroes目录下的所有文件"""
        self.init_dir()  # 初始化目录
        try:
            hero_dir = 'heroes'
            # 收集所有文件
            files_to_process = []
            for old_filename in os.listdir(hero_dir):  # 遍历目录下的所有文件
                files_to_process.append(old_filename)
            asyncio.run(self.process_files_async(files_to_process))  # 使用异步方式处理所有文件
        except KeyboardInterrupt:
            logging.warning("操作被用户中断")
        except Exception as e:
            logging.error(f"处理文件过程中发生错误：{e}")
        finally:
            self.get_runtime()  # 计算运行时间

    async def process_files_async(self, filenames):
        """异步处理所有文件"""
        tasks = []
        for old_filename in filenames:
            logging.info(f"正在读取文件：{old_filename}...")
            task = asyncio.create_task(self.process_single_file(old_filename))
            tasks.append(task)
        # 任务的执行实际上是在 await asyncio.gather(*tasks) 这一行发生的。这行代码会并发执行所有之前创建的任务，并等待它们全部完成
        # 这种异步处理方式比同步方式快得多，因为它可以同时处理多个文件，而不是一个接一个地处理
        await asyncio.gather(*tasks) # 执行并等待所有任务完成

    async def process_single_file(self, old_filename):
        """处理单个文件"""
        hero_dir = 'heroes'
        old_path = os.path.join(hero_dir, old_filename)  # 旧文件路径
        with open(old_path, 'r') as f:
            old_content = f.read()  # 旧内容
            new_content = await self.data_callback_async(old_filename, old_content, self.encipher_async)  # 新内容
            new_filename = old_filename.replace('.txt', '_new.txt')  # 新文件名
        hero_new_dir = 'heroes_new'
        new_path = os.path.join(hero_new_dir, new_filename)  # 新文件路径
        with open(new_path, 'w') as f:
            f.write(new_content)  # 写入新内容
            logging.info(f"文件写入完毕：{new_filename}")

    @staticmethod
    def init_dir():
        if not os.path.exists('heroes_new'):  # 判断目录是否存在
            os.mkdir('heroes_new')  # 创建目录
            logging.info("heroes_new 目录创建完毕！")
        else:
            logging.info("heroes_new 目录已存在！")

    @staticmethod
    def data_callback(old_filename, file_content, callback):  # 数据处理
        logging.info(f"数据处理开始：{old_filename}")
        processed = callback(file_content)  # 回调函数(处理数据)
        logging.info(f"数据处理完毕：{old_filename}")
        return processed

    @staticmethod
    async def data_callback_async(old_filename, file_content, callback):  # 异步数据处理
        logging.info(f"数据处理开始：{old_filename}")
        processed = await callback(file_content)  # 回调函数(处理数据)
        logging.info(f"数据处理完毕：{old_filename}")
        return processed

    @classmethod
    def encipher(cls, file_content):  # 回调函数
        file_content = cls.base64_encode(file_content)
        time.sleep(3)  # 模拟处理数据耗时
        return file_content  # 返回处理后的数据

    @classmethod
    async def encipher_async(cls, file_content):  # 异步回调函数
        base64_str = cls.base64_encode(file_content)  # 进行Base64编码
        encipher_code = cls.custom_encipher(base64_str)  # 进行自定义加密
        await asyncio.sleep(3)  # 模拟处理数据耗时（异步版本）
        return encipher_code  # 返回处理后的数据

    @staticmethod
    def base64_encode(string):
        byte_data = string.encode('utf-8')  # 先将字符串转换为字节（使用utf-8编码）
        base64_encoded = base64.b64encode(byte_data)  # # 进行Base64编码
        base64_str = base64_encoded.decode('utf-8')  # 将字节转换为字符串（使用utf-8解码）
        return base64_str

    @staticmethod
    def custom_encipher(string):
        return "x" + string

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


if __name__ == '__main__':
    hd = HeroData()
    hd.change_hero_data()
