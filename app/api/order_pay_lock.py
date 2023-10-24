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

# 訂單鎖定
class APIOrderPayLock():

    # 請求參數
    class RequestArgs(BaseModel):
        order_no_list : List[str] = Field(examples=[['165277554525515']], description='訂單號列表')
    
    # 回覆參數
    class RespondArgs(BaseModel):
        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')

    @staticmethod
    def handle_request(args : RequestArgs):
        try:
            
            # 更新訂單狀態
            for order_no in args.order_no_list:
                filter = {'order_no' : order_no}
                field_vaules = {'status' : OrderStatus.OS_LOCK}
                SQLiteDB().update(TableAgentOrder._table_name, filter, field_vaules)
                
            # 寫入操作表
            table_operate_log = TableAgentOperateLog()
            table_operate_log.login_time = int(time.time())
            table_operate_log.wallet_address = AppCache().get_login_wallet_address()
            table_operate_log.error_type = OperateErrType.OT_ORDER_PAY

            Logger().logger.info(f'table_operate_log = {table_operate_log.to_dict()}')
            SQLiteDB().insert(TableAgentOperateLog._table_name, table_operate_log.to_dict())

            return Exceptions.ERR_OK

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return Exceptions.ERR_SERVER
