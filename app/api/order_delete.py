# -*- coding:utf-8 -*-
import time
import traceback
from typing import List
from pydantic import BaseModel, Field
from utils.logger import Logger
from db.sqlitedb import SQLiteDB
from db.table import TableAgentOrder
from .base import OrderDel
from core.exceptions import Exceptions

# 訂單完成
class APIOrderDelete():

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
            # 刪除訂單, 物理删除, 删除后可以导入之前删除了的订单号
            for order_no in args.order_no_list:
                filter = {'order_no' : order_no}
                SQLiteDB().delete(TableAgentOrder._table_name, filter)

            return Exceptions.ERR_OK

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return Exceptions.ERR_SERVER
