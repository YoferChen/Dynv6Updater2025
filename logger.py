import logging
from logging import handlers
from logging import Logger  as BaseLogger
import os


class Logger:
    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, level='info', when='D', back_count=3,
                 fmt='%(asctime)s - %(pathname)s [%(funcName)s/line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger: BaseLogger = None
        self.fmt = fmt
        self.level = level
        self.when = when
        self.back_count = back_count

    def start(self, file_path='./logger.log'):
        self.file_path = file_path
        # 创建日志文件
        self.logger = logging.getLogger(file_path)
        format_str = logging.Formatter(self.fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(self.level))  # 设置日志级别
        stream_handler = logging.StreamHandler()  # 往屏幕上输出
        stream_handler.setFormatter(format_str)  # 设置屏幕上显示的格式
        self.logger.addHandler(stream_handler)  # 把对象加到logger里
        # 日志写入文件
        '''
        实例化TimedRotatingFileHandler
        interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        S 秒
        M 分
        H 小时
        D 天
        W 每星期（interval==0时代表星期一）
        midnight 每天凌晨
        '''
        if file_path is not None:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            time_file_handler = handlers.TimedRotatingFileHandler(filename=file_path, when=self.when,
                                                                  backupCount=self.back_count,
                                                                  encoding='utf-8')
            time_file_handler.setFormatter(format_str)  # 设置文件里写入的格式
            self.logger.addHandler(time_file_handler)

    def __call__(self, msg: str, mode='info'):
        if mode == 'info':
            self.logger.info(msg)

logger = Logger()
# if __name__ == '__main__':
#     logger = Logger()
