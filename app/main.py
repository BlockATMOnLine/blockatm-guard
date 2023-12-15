# -*- coding:utf-8 -*-
import os
import sys
import time
import threading
import json
import requests
import yaml
import traceback
import uuid
import webview
import platform
from db.sqlitedb import SQLiteDB
from db.table import TableAgentConfig
from utils.logger import Logger
from utils.tool import get_free_port, OSName, get_work_dir
from utils.crypto_engine import AESEngine
from core.config import VERSION_TYPE
from core.setting import VersionType
from agent.agent_server import AgentServer

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
        update_conf_url = agent_config.get('update_conf_url', '')
        url = f'{update_conf_url}/{yaml_file}'

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

        else:
            Logger().logger.info(f'Already the latest configuration, no need to update!')

    except Exception as err:
        Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

# 推送登出
def push_log_out(host : str, port : int):
    # 推送登出
    url = f'http://{host}:{port}/v1/agent/logout'
    # 本地禁用代理
    proxies = {
        "http": "",
        "https": "",
    }
    respond = requests.post(url, proxies=proxies)
    Logger().logger.info(f'logout respond = {respond.text}')
    
def main():
    try:
        # 初始化日誌
        # log_level = 'debug'
        # if VERSION_TYPE == VersionType.VT_RELEASE:
        #     log_level = 'info'
        
        log_level = 'info'
        if platform.system() == OSName.OS_WINDOWS:
            Logger().init('blockatm-guard', './logs', level=log_level)
        else:
            Logger().init('blockatm-guard', os.path.join(get_work_dir(), 'logs'), level=log_level)

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
            Logger().logger.info('Sqlit db config is empty! Please make sure the database file exists!')
            
        table = TableAgentConfig().assignment(data_list[0])
        config = json.loads(table.config)
        front_version = table.front_version
        
        if not config:
            Logger().logger.error(f'confg is null! close app')
                
        Logger().logger.debug(f'config = {config}')
        
        # 啟動server
        thread_server = threading.Thread(target=AgentServer().run, kwargs={'host' : host, 'port' : port, 'config':config, 'front_version':front_version, 'process_token':process_token})
        thread_server.setDaemon(True)
        thread_server.start()

        # 檢測更新
        if VERSION_TYPE == VersionType.VT_RELEASE:
            thread_update = threading.Thread(target=check_app_update, args=(host, port, table, process_token))
            thread_update.setDaemon(True)
            thread_update.start()
        
        # mac啟動較慢
        if platform.system() == OSName.OS_MAC:
            time.sleep(1)

        # 啟動客戶端
        Logger().logger.info('AgentMainWindow start')
        #webview.create_window('BlockATM-Guard', f'http://{host}:{port}/index.html', width=1140, height=750, confirm_close=True, min_size = (1140, 750), minimized=True)
        webview.create_window('BlockATM-Guard', f'http://{host}:{port}/index.html', width=1140, height=750, confirm_close=True, min_size = (1140, 750))
        webview.start(localization={'global.quitConfirmation': '是否確認關閉?'})
        Logger().logger.info('AgentMainWindow close')

        # 推送登出
        push_log_out(host, port)
        
        Logger().logger.info("blockatm-guard end")

    except Exception as err:
        Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

if __name__ == '__main__':
    # 多進程打包必加
    #multiprocessing.freeze_support()
    sys.exit(main())