# -*- coding:utf-8 -*-
import traceback
import uuid
import time
from pydantic import BaseModel, Field
from utils.logger import Logger
from utils.tool import get_mac_address
from db.sqlitedb import SQLiteDB
from db.table import TableAgentLoginLog, TableAgentOperateLog
from core.exceptions import Exceptions
from .base import OperateErrType
from utils.cache import AppCache

class APILogout():

    # 回覆參數
    class RespondArgs(BaseModel):
        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')

    @staticmethod
    def handle_request():
        try:
            if AppCache().get_token():
                SQLiteDB().update(TableAgentLoginLog._table_name, {'token':AppCache().get_token()}, {'logout_time':int(time.time())})
            
            AppCache().reinit()
            
            return Exceptions.ERR_OK

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return Exceptions.ERR_SERVER
            




