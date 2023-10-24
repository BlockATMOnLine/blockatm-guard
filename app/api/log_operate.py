# -*- coding:utf-8 -*-
import traceback
from typing import List
from pydantic import BaseModel, Field
from utils.logger import Logger
from db.sqlitedb import SQLiteDB
from db.table import TableAgentOperateLog
from core.exceptions import Exceptions

# 查詢操作日誌
class APIQueryOperateLog():
    
    class RespondArgs(BaseModel):
        # 登錄日誌數據
        class Data(BaseModel):
            class Log(BaseModel):
                login_time : int = Field(description = '登錄時間, 秒級時間戳')
                wallet_address : str = Field(examples=['0x54F5D'],description='錢包地址')
                error_type : str = Field(examples=['Login Success!'],description = '錯誤類型')
            
            logs : List[Log] = Field(description='登錄日誌數據')

        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')
        data : Data = None

    @staticmethod
    def handle_request():
        try:
            # 查詢登錄日誌
            res_list = SQLiteDB().query(TableAgentOperateLog._table_name, desc=True)
            if not isinstance(res_list, list):
                return Exceptions.ERR_DB
            
            log_list = []
            for db_res in res_list:
                operate_log = TableAgentOperateLog()
                operate_log.assignment(db_res)

                log = APIQueryOperateLog.RespondArgs.Data.Log(**operate_log.to_dict())
                log_list.append(log)

            data = APIQueryOperateLog.RespondArgs.Data(logs=log_list)

            return Exceptions.ERR_OK, data.model_dump()

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return Exceptions.ERR_SERVER