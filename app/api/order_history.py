# -*- coding:utf-8 -*-
import traceback
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from utils.logger import Logger
from db.sqlitedb import SQLiteDB
from db.table import TableAgentHistoryOrder
from .base import OrderStatus
from core.exceptions import Exceptions
from utils.cache import AppCache

class APIOrderHistory():

    # 請求參數
    class RequestArgs(BaseModel):
        time_start : int = Field(examples=[1695815749], description='開始時間，秒級時間戳，沒有填0')
        time_end : int = Field(examples=[1695815749], description='結束時間，秒級時間戳，沒有填0')
        order_no : str= Field(examples=['165277554525515'], description='訂單號')
        crypto : str= Field(examples=['USDT'], description='數字幣code')
        network : str = Field(examples=['Ethereum'], description='數字幣網絡')
        amount_start : str= Field(examples=['32.22'], description='訂單金額最小值，沒有填0')
        amount_end : str= Field(examples=['32.22'], description='訂單金額範圍最大值，沒有填0')
        uid : str= Field(examples=['00000012'], description='')
        biz_name : str= Field(examples=['MPay'], description='業務名稱')
        wallet_address : str = Field(examples=['0x54F5D'],description='錢包地址')
    
    # 回覆參數
    class RespondArgs(BaseModel):
        
        # 數據
        class Data(BaseModel):
            # 訂單數據
            class Order(BaseModel):
                order_no : str = Field(examples=['12533363552222'], description='訂單號')
                order_date : int = Field(examples=[1695815749],description='訂單時間，秒級時間戳')
                import_date : int = Field(examples=[1695815749],description='導入時間，秒級時間戳')
                finish_date : int = Field(examples=[1695815749],description='完成時間，秒級時間戳')
                crypto : str = Field(examples=['USDT'],description='數字幣code')
                network : str = Field(examples=['Ethereum'],description='數字幣網絡')
                wallet_address : str = Field(examples=['0x54F5D'],description='收款地址')
                amount : str = Field(examples=['33.20'],description='訂單金額')
                uid : str = Field(examples=['00000012'],description='UID')
                biz_name : str = Field(examples=['Mpay'],description='業務名稱')

            orders : List[Order] = Field(description='訂單數據')

        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')
        data : Data = None


    @staticmethod
    def handle_request(args : RequestArgs):
        try:
            
            sql = f'''select * from {TableAgentHistoryOrder._table_name} where 1 = 1 '''
            if args.time_start:
                sql += f' and order_date >= {args.time_start} '
            
            if args.time_end:
                sql += f' and order_date <= {args.time_end} '

            if args.order_no:
                sql += f' and order_no = \'{args.order_no}\''
            
            if args.crypto:
                sql += f' and crypto = \'{args.crypto}\''
            
            if args.network:
                sql += f' and network = \'{args.network}\''
            
            if args.amount_start:
                sql += f' and cast(amount as decimal(18,12)) >= {args.amount_start}'
            
            if args.amount_end:
                sql += f' and cast(amount as decimal(18,12)) <= {args.amount_end}'
            
            if args.uid:
                sql += f' and uid = \'{args.uid}\''
            
            if args.biz_name:
                sql += f' and biz_name = \'{args.biz_name}\''
            
            if args.wallet_address:
                sql += f' and wallet_address = \'{args.wallet_address}\''
            
            sql += ' order by finish_date desc'

            res_list = SQLiteDB().query_sql(sql)
            
            Logger().logger.error(f'res_list = {res_list}')

            # 校驗數據結果
            if not isinstance(res_list, list):
                return Exceptions.ERR_DB

            # 訂單數據
            order_list = []
            for db_res in res_list:
                order = TableAgentHistoryOrder()
                order.assignment(db_res)

                # network篩選
                if order.network != AppCache().get_login_network():
                    continue
                
                order = APIOrderHistory.RespondArgs.Data.Order(**order.to_dict())
                order_list.append(order)
            
            data = APIOrderHistory.RespondArgs.Data(orders=order_list)
            
            return Exceptions.ERR_OK, data.model_dump()

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return Exceptions.ERR_SERVER
