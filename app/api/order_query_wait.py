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
from utils.cache import AppCache

# 查詢待支付訂單
class APIOrderQueryWait():
    
    # 回覆參數
    class RespondArgs(BaseModel):
        # 數據
        class Data(BaseModel):
            # 訂單數據
            class Order(BaseModel):
                order_no : str = Field(examples=['12533363552222'], description='訂單號')
                order_date : int = Field(examples=[1695815749],description='訂單時間，秒級時間戳')
                import_date : int = Field(examples=[1695815749],description='導入時間，秒級時間戳')
                crypto : str = Field(examples=['USDT'],description='數字幣code')
                network : str = Field(examples=['Ethereum'],description='數字幣網絡')
                wallet_address : str = Field(examples=['0x54F5D'],description='收款地址')
                amount : str = Field(examples=['33.20'],description='訂單金額')
                uid : str = Field(examples=['00000012'],description='UID')
                biz_name : str = Field(examples=['Mpay'],description='業務名稱')
                status : int = Field(examples=[1],description='訂單狀態: 0-未支付, 1-鎖定, 2-上鍊')
                txid : str = Field(examples=['fdaf-fdaf'], description='txid')
                is_del : int = Field(examples=[0], description='是否刪除:0-未刪除')
            
            orders : List[Order] = Field(description='訂單數據')
                
        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')
        data : Data = None

    @staticmethod
    def handle_request():
        try:
            out_time = int(time.time()) - 30 * 24 * 3600
            # 刪除導入日誌超過1個月的訂單
            Logger().logger.info('delete improt time out order!')
            SQLiteDB().delete(TableAgentOrder._table_name, [f'import_date < {out_time}'])

            # 查詢訂單
            filter = ['status in (0,1,2)', 'is_del=0', f'import_date >= {out_time}']
            res_list = SQLiteDB().query(TableAgentOrder._table_name, filter, sort_field=['order_date'], desc=True)

            # 校驗數據結果
            if not isinstance(res_list, list):
                return Exceptions.ERR_DB
            
            order_list = []
            for res in res_list:
                table_order = TableAgentOrder()
                table_order.assignment(res)

                # network篩選
                if table_order.network != AppCache().get_login_network():
                    continue

                order = APIOrderQueryWait.RespondArgs.Data.Order(**table_order.to_dict())

                order_list.append(order)
            
            data = APIOrderQueryWait.RespondArgs.Data(orders=order_list).model_dump()
            
            return Exceptions.ERR_OK, data

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return Exceptions.ERR_SERVER
