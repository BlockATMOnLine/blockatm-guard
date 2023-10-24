# -*- coding:utf-8 -*-
import traceback
from typing import List
from pydantic import BaseModel, Field
from utils.logger import Logger
from db.sqlitedb import SQLiteDB
from db.table import TableAgentLoginLog
from core.exceptions import Exceptions

# 查詢登錄日誌
class APIQueryLoginLog():

    class RespondArgs(BaseModel):
        # 登錄日誌數據
        class Data(BaseModel):
            class Log(BaseModel):
                token : str = Field(examples=['c2ec3e44'], description='請求憑證')
                login_time : int = Field(examples=[1695815749],description = '登錄時間, 秒級時間戳')
                logout_time : int = Field(examples=[1695815749],description = '登出時間, 秒級時間戳')
                wallet_address : str = Field(examples=['0x54F5D'],description='錢包地址')
                mac : str = Field(examples=['09-45-d1-p2'],description = '設備mac')
            
            logs : List[Log] = Field(description='登錄日誌數據')

        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')
        data : Data = None

    @staticmethod
    def handle_request():
        try:
            # 查詢登錄日誌
            res_list = SQLiteDB().query(TableAgentLoginLog._table_name, desc=True)
            if not isinstance(res_list, list):
                return Exceptions.ERR_DB
            
            log_list = []
            for db_res in res_list:
                loginlog = TableAgentLoginLog()
                loginlog.assignment(db_res)
                log = APIQueryLoginLog.RespondArgs.Data.Log(**loginlog.to_dict())
                log_list.append(log)

            data = APIQueryLoginLog.RespondArgs.Data(logs=log_list)

            return Exceptions.ERR_OK, data.model_dump()

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return Exceptions.ERR_SERVER