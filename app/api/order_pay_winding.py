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

# 訂單上鍊
class APIOrderPayWinding():

    # 請求參數
    class RequestArgs(BaseModel):
        order_no_list : List[str] = Field(examples=[['165277554525515']], description='訂單號列表')
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
            for order_no in args.order_no_list:
                filter = {'order_no' : order_no}
                field_vaules = {'status' : OrderStatus.OS_WINDING, "txid" : args.txid}
                SQLiteDB().update(TableAgentOrder._table_name, filter, field_vaules)
                
            return Exceptions.ERR_OK

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return Exceptions.ERR_SERVER
