# -*- coding:utf-8 -*-
import traceback
import json
import uuid
import time
from pydantic import BaseModel, Field
from utils.logger import Logger
from utils.tool import get_mac_address
from db.sqlitedb import SQLiteDB
from db.table import TableAgentConfig, TableAgentOperateLog
from core.exceptions import Exceptions
from .base import OperateErrType
from utils.cache import AppCache

class APIConfigUpdate():
        
    # 回覆參數
    class RespondArgs(BaseModel):
        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')

    @staticmethod
    def handle_request(config : str):
        try:
            # 寫入更新配置到數據庫
            Logger().logger.info('config update!')

            field_vaules = {
                "config" : config,
                'update_time' : int(time.time())
            }
            SQLiteDB().update(TableAgentConfig._table_name, filter={}, field_vaules=field_vaules)

            # 更新到cash
            AppCache().config_update(json.loads(config))

            return Exceptions.ERR_OK
            
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return Exceptions.ERR_SERVER
            

