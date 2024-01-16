# -*- coding:utf-8 -*-
import traceback
import os
import time
from typing import List
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from fastapi import UploadFile
from utils.logger import Logger
from utils.tool import get_run_dir
from core.exceptions import Exceptions
from utils.cache import AppCache

# 下載訂單模板
class APIOrderDownloadTemplate():
    
    @staticmethod
    def handle_request(random : str):
        try:
            login_chainid:str = AppCache().get_login_chain()
            login_network:str = AppCache().get_chain_network(login_chainid)
            
            Logger().logger.info(f'random = {random}, login_chainid = {login_chainid}, login_network = {login_network}')
            
            filename = f'BlockTemplate_{login_network.replace(" ", "")}.xlsx'
            file_path = f'{get_run_dir()}/templates/BlockTemplate_ChainID_{login_chainid}.xlsx'

            Logger().logger.info(f'file_path = {file_path}, filename = {filename}')

            Logger().logger.info("download order template")
            return FileResponse(path=file_path, filename=filename)
        
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
