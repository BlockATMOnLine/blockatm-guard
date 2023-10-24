# -*- coding:utf-8 -*-
import sys
import os
import signal
import time
import threading
import json
import requests
import yaml
import traceback
import uuid
import platform
import multiprocessing
from db.sqlitedb import SQLiteDB
from db.table import TableAgentConfig
from utils.logger import Logger
from utils.tool import get_free_port, check_free_port, OSName
from utils.crypto_engine import AESEngine
from core.config import VERSION_TYPE
from core.setting import VersionType
from PyQt5.QtWidgets import QApplication, QMessageBox
from agent.agent_server import AgentServer
from agent.agent_windows import AgentMainWindow

def show_error_windows(title : str, text : str):
    app = QApplication(sys.argv)
    #window = QMessageBox.question(None, title, text)
    window = QMessageBox(text=text)
    window.show()
    app.exec()

# 更新檢測
def check_app_update(host, port, table : TableAgentConfig, process_token : str)->dict:
    Logger().logger.info('check_app_update')
    agent_config = table.to_dict()
    
    aes_key = table.aes_key
    config = json.loads(table.config)
    version = config.get('version', 0)

    if not aes_key:
        Logger().logger.error('encryption key not found!')
        return
    
    try:
        # 獲取github線上文件數據
        yaml_file = agent_config.get('yaml_file', '')
        url = f'https://github.com/BlockATMOnLine/desktop-agent-action/raw/main/configurations/{yaml_file}'

        res = requests.get(url, timeout=(5, 10))

        Logger().logger.debug(f'res = {res.text}')

        if not res.ok:
            Logger().logger.error('failed to update configuration. Please make sure you can connect to github.com normally!')
            
        # 解密
        decrypt_text = AESEngine.aesdecrypt(aes_key, res.text)
        update_config : dict = yaml.safe_load(decrypt_text)
        update_version = update_config.get('version', 0)

        Logger().logger.debug(f'update_config = {update_config}')

        if update_version and update_version > version:

            Logger().logger.info(f'push update_config')

            # 將配置推送到server
            url = f"http://{host}:{port}/v1/agent/config_update"

            payload = {
                "config": json.dumps(update_config)
            }

            headers = {
                'accept': 'application/json',
                'process-token': process_token,
                'Content-Type': 'application/json'
            }
            
            # 本地禁用代理
            proxies = {
                "http": "",
                "https": "",
            }
            response = requests.get(url, headers=headers, params=payload, proxies=proxies)

            Logger().logger.info(f'response = {response.text}')

    except Exception as err:
        Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
    
def main():
    try:
        # 初始化日誌
        if VERSION_TYPE == VersionType.VT_RELEASE:
            Logger().init('blockatm-guard', './logs', level='info')
        else:
            Logger().init('blockatm-guard', './logs', level='debug')
        
        Logger().logger.info("-----------------------------------------------------------")
        Logger().logger.info("blockatm-guard start")

        # 獲取監聽端口
        #host = '127.0.0.1'
        host = 'localhost'
        port = get_free_port()
        process_token = str(uuid.uuid4())

        # 讀取數據庫
        data_list : list = SQLiteDB().query_sql('select * from agent_config order by update_time desc limit 1;')
        if not isinstance(data_list, list) or not data_list:
            show_error_windows('Error', 'Sqlit db config is empty! Please make sure the database file exists!')
            return
            
        table = TableAgentConfig().assignment(data_list[0])
        config = json.loads(table.config)
        
        if not config:
            Logger().logger.error(f'confg is null! close app')
            return
                
        Logger().logger.debug(f'config = {config}')
        
        # 啟動server
        process_server = multiprocessing.Process(target=AgentServer().run, kwargs={'host' : host, 'port' : port, 'config':config, 'process_token':process_token})
        process_server.start()

        #process_server.join()

        # 檢測更新
        if VERSION_TYPE == VersionType.VT_RELEASE:
            thread = threading.Thread(target=check_app_update, args=(host, port, table, process_token))
            thread.start()
        
        if platform.system() == OSName.OS_WINDOWS:
            signal_stop = signal.CTRL_C_EVENT
        else:
            signal_stop = signal.SIGINFO

        # 啟動客戶端
        Logger().logger.info('AgentMainWindow start')
        app = QApplication(sys.argv)
        window = AgentMainWindow(host=host, port=port)
        window.show()
        app.exec()
        Logger().logger.info('AgentMainWindow close')
            
        # 關閉server
        os.kill(process_server.pid, signal_stop)
        time.sleep(2)
        #process_server.join()
        process_server.kill()

        Logger().logger.info("blockatm-guard end")

    except Exception as err:
        Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

if __name__ == '__main__':
    # 多進程打包必加
    multiprocessing.freeze_support()
    sys.exit(main())