import logging
import os
import webbrowser
import time
from logging import handlers

class Logger(object):
    # 日誌級別關係映射
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }

    # 日誌切割模式
    time_mode = {
        'S',            # 秒
        'M',            # 分鐘
        'H',            # 小時
        'D',            # 天
        'W',            # 星期
        'midnight'      # 每天凌晨
    }

    # 單列模式
    _instance = None
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance
    
    # 獲取logger
    @property
    def logger(self):
        return self._logger

    # 初始化
    def init(self, name, path = '', level = 'info', when = 'D', back_count = 0, fmt='[%(asctime)s][%(filename)s:%(lineno)d:%(funcName)s()][%(levelname)s]: %(message)s'):
        try:
            # 日誌
            self._logger = logging.getLogger(name)

            # 設置日誌格式
            format_str = logging.Formatter(fmt)
            # 設置日誌級別
            self._logger.setLevel(self.level_relations.get(level))
            
            # 設置屏幕輸出
            sh = logging.StreamHandler()
            sh.setFormatter(format_str)
            self._logger.addHandler(sh)

            if(os.path.exists(path) == False):
                os.makedirs(path)
            
            # 設置文件輸出
            filepath = ''
            t = time.strftime('%Y%m%d', time.localtime(time.time()))
            if path and path[-1] != '/':
                filepath = "{}/{}{}.log".format(path, name, t)
            else:
                filepath = "{}{}{}.log".format(path, name, t)

            th = handlers.TimedRotatingFileHandler(filename = filepath, when = when, backupCount = back_count, encoding='utf-8')#往文件裡寫入#指定間隔時間自動生成文件的處理器
            th.setFormatter(format_str)
            self._logger.addHandler(th)

        except Exception as err:
            pass
            # url = f'{path}'
            # webbrowser.open(f'http://{url}')