# -*- coding:utf-8 -*-
import io
import re
import typing
import time
import traceback
import msoffcrypto
import pandas
import math
from msoffcrypto.exceptions import InvalidKeyError
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import UploadFile
from .base import OrderStatus
from utils.logger import Logger
from utils.tool import datetime_object_to_second_timestamp, check_amount
from utils.cache import AppCache
from db.sqlitedb import SQLiteDB
from db.table import TableAgentOrder, TableAgentHistoryOrder
from core.exceptions import Exceptions
from core.setting import NetWorkType, NetWorkRegular

# 導入訂單excel文件
class APIOrderUpload():
    
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
    def handle_request(file: UploadFile, file_password : str):
        try:
            
            # 讀取excel數據
            res = APIOrderUpload.read_excel(file.file, file_password)

            if not isinstance(res, list):
                Logger().logger.error('read excel file fail')
                if res == 1:
                    return Exceptions.ERR_EXCEL_PASSWORD
                elif res == 2:
                    return Exceptions.ERR_READ_EXCEL_ERROR
                elif res == 3:
                    return Exceptions.ERR_UPLOAD_VALUES_ORDER_DATE_FORMAT
                elif res == 4:
                    return Exceptions.ERR_UPLOAD_ORDER_NO_EMPTY
                
                return Exceptions.ERR_READ_EXCEL_ERROR
            
            upload_order_list : List[TableAgentOrder] = res

            # 檢驗order數據
            for upload_order in upload_order_list:

                # 訂單號和業務名稱不能同時為空
                if not upload_order.order_no:
                    Logger().logger.error("order no cannot be empty")
                    return Exceptions.ERR_UPLOAD_ORDER_NO_EMPTY
                
                if upload_order.network != AppCache().get_login_network():
                    Logger().logger.error("order network not match current login network")
                    return Exceptions.ERR_UPLOAD_NETWORK_NO_MATCH
                
                if '|' in upload_order.biz_name+upload_order.order_no+upload_order.uid+upload_order.network+upload_order.wallet_address+upload_order.amount+upload_order.crypto:
                    Logger().logger.error("uploaded data contains the '|' character")
                    return Exceptions.ERR_UPLOAD_VALUES_HAVE_CHAR
                
                if not check_amount(upload_order.amount):
                    Logger().logger.error('amount field is not a number or floating point number')
                    return Exceptions.ERR_UPLOAD_VALUES_AMOUNT_NOT_NUMBER
                
                # 訂單號不能超過30個字符
                if len(upload_order.order_no) > 30:
                    Logger().logger.error('The order no field cannot exceed 30 characters')
                    return Exceptions.ERR_UPLOAD_ORDER_NO_LEN_LIMIT_30

                # 業務名稱不能超過30個字符
                if len(upload_order.biz_name) > 30:
                    Logger().logger.error('The business name field cannot exceed 30 characters')
                    return Exceptions.ERR_UPLOAD_BUSINESS_NAME_LEN_LIMIT_30
                
                # 訂單號不能含有'.'字符
                if '.' in upload_order.order_no:
                    Logger().logger.error('The order no cannot contain the . character')
                    return Exceptions.ERR_UPLOAD_ORDER_NO_CONTAIN_POINT_CHAR

                # 業務名稱不能含有'.'字符
                if '.' in upload_order.biz_name:
                    Logger().logger.error('The business name cannot contain the . characters')
                    return Exceptions.ERR_UPLOAD_BUSINESS_NAME_CONTAIN_POINT_CHAR
                
                # 校驗錢包地址格式
                if NetWorkType.NWT_ETH == AppCache().get_login_network():
                    if not re.match(NetWorkRegular.NWR_ETH, upload_order.wallet_address):
                        Logger().logger.error('wallet address format error')
                        return Exceptions.ERR_UPLOAD_VALUES_WALLET_ADDRESS_FORMAT
                
                if NetWorkType.NWT_TRON == AppCache().get_login_network():
                    if not re.match(NetWorkRegular.NWR_TRON, upload_order.wallet_address):
                        Logger().logger.error('wallet address format error')
                        return Exceptions.ERR_UPLOAD_VALUES_WALLET_ADDRESS_FORMAT
                
                res_list = SQLiteDB().query(TableAgentOrder._table_name, filter={'order_no':upload_order.order_no})
                Logger().logger.info(f'res_list = {res_list}')
                if isinstance(res_list, list) and res_list:
                    return Exceptions.ERR_UPLOAD_ORDER_NO_EXIST
                
                res_list = SQLiteDB().query(TableAgentHistoryOrder._table_name, filter={'order_no':upload_order.order_no})
                Logger().logger.info(f'res_list = {res_list}')
                if isinstance(res_list, list) and res_list:
                    return Exceptions.ERR_UPLOAD_ORDER_NO_EXIST_IN_HISTORY
                
            # 保存到數據庫
            respond_order_list = []
            for upload_order in upload_order_list:
                SQLiteDB().insert(TableAgentOrder._table_name, upload_order.to_dict())
                
                respond_order = APIOrderUpload.RespondArgs.Data.Order(**upload_order.to_dict())
                respond_order_list.append(respond_order)
            
            data = APIOrderUpload.RespondArgs.Data(orders=respond_order_list)
                
            return Exceptions.ERR_OK, data.model_dump()
        
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return Exceptions.ERR_SERVER
    
    
    # 讀取excel
    @staticmethod
    def read_excel(file : typing.BinaryIO, file_password : str)->List[RespondArgs.Data]:
        try:
            # 解密
            read_io = io.BytesIO()
            excel = msoffcrypto.OfficeFile(file)
            excel.load_key(file_password)
            excel.decrypt(read_io)
            
            #df : pd.DataFrame = pd.read_excel(read_io, sheet_name='Orders', skiprows = [0])
            df : pandas.DataFrame = pandas.read_excel(read_io, sheet_name='Orders', skiprows = [0])

            upload_order_list = []
            for line in df.values:
                Logger().logger.info(f'line = {line}')
                table_order = TableAgentOrder()
                
                try:
                    table_order.order_date = datetime_object_to_second_timestamp(line[0].to_pydatetime())
                except Exception as err:
                    Logger().logger.error('order_date format error!')
                    Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
                    return 3
                
                table_order.biz_name = str(line[1])
                table_order.order_no = str(line[2])
                if isinstance(line[2], float) and math.isnan(line[2]):
                    Logger().logger.error('order no is nan')
                    return 4
                Logger().logger.info(f'type uid = {type(line[3])}, value = {line[3]}')
                table_order.uid = str(line[3])
                table_order.network = str(line[4])
                table_order.wallet_address = str(line[5])
                table_order.amount = str(line[6])
                table_order.crypto = str(line[7])
                table_order.import_date = int(time.time())
                table_order.status = OrderStatus.OS_NOT_PROCESS
                table_order.txid = ''
                table_order.is_del = 0
                
                Logger().logger.info(f'order_list = {table_order.__dict__}')

                upload_order_list.append(table_order)
            
            return upload_order_list
        except InvalidKeyError as err:
            Logger().logger.error('excel password error!')
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return 1
        except Exception as err:
            Logger().logger.error('read excel error!')
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return 2

