# -*- coding:utf-8 -*-
import time
import traceback
from pydantic import BaseModel, Field
from utils.logger import Logger
from db.sqlitedb import SQLiteDB
from db.table import TableAgentOrder, TableAgentHistoryOrder
from .base import OrderStatus, OrderDel
from core.exceptions import Exceptions
from utils.cache import AppCache

# 訂單完成
class APIOrderPaySuccess():

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
            
            # 添加到歷史訂單
            res_list = SQLiteDB().query(TableAgentOrder._table_name, {'txid':args.txid,'is_del' : OrderDel.OD_NOT_DEL})
            for res in res_list:
                table_order = TableAgentOrder()
                table_order.assignment(res)

                table_his_order = TableAgentHistoryOrder()
                table_his_order.order_no : str = table_order.order_no
                table_his_order.order_date : int = table_order.order_date
                table_his_order.import_date : int = table_order.import_date
                table_his_order.finish_date : int = int(time.time())
                table_his_order.crypto : str = table_order.crypto
                table_his_order.chainid : str = table_order.chainid
                table_his_order.network : str = table_order.network
                table_his_order.wallet_address : str = table_order.wallet_address
                table_his_order.amount : str = table_order.amount
                table_his_order.uid : str = table_order.uid
                table_his_order.biz_name : str = table_order.biz_name
                table_his_order.txid : str = table_order.txid

                SQLiteDB().insert(TableAgentHistoryOrder._table_name, table_his_order.to_dict())
                
            # 更新訂單狀態
            filter = {'txid' : args.txid}
            field_vaules = {'status' : OrderStatus.OS_FINISH, 'is_del' : OrderDel.OD_DEL}
            SQLiteDB().update(TableAgentOrder._table_name, filter, field_vaules)

            return Exceptions.ERR_OK

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return Exceptions.ERR_SERVER
