# -*- coding:utf-8 -*-
import time
import traceback
from typing import List
from pydantic import BaseModel, Field
from utils.logger import Logger
from db.sqlitedb import SQLiteDB
from db.table import TableAgentOrder, TableAgentOperateLog
from .base import OrderStatus, OperateErrType
from core.exceptions import Exceptions
from utils.cache import AppCache

# 訂單完成
class APIOrderPayFail():

    # 請求參數
    class RequestArgs(BaseModel):
        txid : str = Field(examples=['fdaf-fdaf'], description='txid')
    
    # 回覆參數
    class RespondArgs(BaseModel):
        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')

    @staticmethod
    def handle_request(args : RequestArgs):
        try:
            Logger().logger.info(f'order pay fail, txid = {args.txid}')

            # 更新訂單狀態
            filter = {'txid' : args.txid}
            field_vaules = {'status' : OrderStatus.OS_NOT_PROCESS, 'txid':''}
            SQLiteDB().update(TableAgentOrder._table_name, filter, field_vaules)

                
            return Exceptions.ERR_OK

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return Exceptions.ERR_SERVER
