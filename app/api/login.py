# -*- coding:utf-8 -*-
import traceback
import uuid
import time
from pydantic import BaseModel, Field
from utils.logger import Logger
from utils.tool import get_mac_address
from db.sqlitedb import SQLiteDB
from db.table import TableAgentLoginLog, TableAgentOperateLog
from core.exceptions import Exceptions
from .base import OperateErrType
from utils.cache import AppCache

class APILogin():
    # 請求參數
    class RequestArgs(BaseModel):
        chainid : str = Field(examples=['5'],description='链路')
        # network : str = Field(examples=['Torn'],description='網絡')
        wallet_address : str = Field(examples=['TCXJJvq1F8YHN5uXs4UhTUmN8RFUxs2Zd2'],description='錢包地址')
        
    # 回覆參數
    class RespondArgs(BaseModel):
        class Data(BaseModel):
            token : str = Field(examples=['c2ec3e44'],description='請求憑證')
            contract_address : str = Field(examples=['0x54F5D'],description='合約地址')

        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')
        data : Data = None

    @staticmethod
    def handle_request(args : RequestArgs):
        try:
            is_success = False

            Logger().logger.debug(f'login: args = {args}')

            # 判斷network是否能登錄
            if args.chainid not in AppCache().get_chain_list():
                Logger().logger.error('chainid not support!')
                return Exceptions.ERR_NETWORK_NOT_SUPPORT
            
            # 判斷wallet_address是否能登錄
            if args.wallet_address not in AppCache().get_chain_wallet_address(args.chainid):
                Logger().logger.error('this wallet address can not login!')
                return Exceptions.ERR_WALLET_ADDRESS_NOT_SUPPORT
                
            contract_address = AppCache().get_chain_contract_address(args.chainid)
            if not contract_address:
                Logger().logger.error('this wallet address can not login!')
                return Exceptions.ERR_CONTRACT_ADDRESS_NULL
            
            # 重複登錄
            if AppCache().get_token():
                SQLiteDB().update(TableAgentLoginLog._table_name, {'token':AppCache().get_token()}, {'logout_time':int(time.time())})

            # 保存緩存
            token = str(uuid.uuid4())
            AppCache().reinit()
            AppCache().set_token(token)
            AppCache().set_login_chain(args.chainid)
            AppCache().set_login_wallet_address(args.wallet_address)

            is_success = True
            return Exceptions.ERR_OK, APILogin.RespondArgs.Data(token=token, contract_address=contract_address).model_dump()

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return Exceptions.ERR_SERVER
            
        finally:
            # 寫入登錄日誌表
            if is_success:
                table_login_log = TableAgentLoginLog()
                table_login_log.token = AppCache().get_token()
                table_login_log.login_time = int(time.time())
                table_login_log.logout_time = int(time.time()) + 60
                table_login_log.wallet_address = args.wallet_address
                table_login_log.mac = get_mac_address()
                Logger().logger.info(f'table_login_log = {table_login_log.to_dict()}')
                SQLiteDB().insert(TableAgentLoginLog._table_name, table_login_log.to_dict())
            
            # 寫入操作表
            table_operate_log = TableAgentOperateLog()
            table_operate_log.login_time = int(time.time())
            table_operate_log.wallet_address = args.wallet_address
            table_operate_log.error_type = OperateErrType.OT_LOGIN_SUCCESS if is_success else OperateErrType.OT_LOGIN_FAIL
            
            Logger().logger.info(f'table_operate_log = {table_operate_log.to_dict()}')
            SQLiteDB().insert(TableAgentOperateLog._table_name, table_operate_log.to_dict())
            




