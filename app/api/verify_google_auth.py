# -*- coding:utf-8 -*-
import traceback
import time
import pyotp
from pydantic import BaseModel, Field
from utils.logger import Logger
from db.sqlitedb import SQLiteDB
from db.table import TableAgentOperateLog
from core.exceptions import Exceptions
from .base import OperateErrType
from utils.cache import AppCache

# 谷歌auth驗證
class APIVerifyGoogleAuth():

    # 請求參數
    class RequestArgs(BaseModel):
        verify_code : str = Field(examples=['256501'], description='谷歌auth驗證碼')

    # 回覆參數
    class RespondArgs(BaseModel):
        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')

    @staticmethod
    def handle_request(args : RequestArgs):
        try:
            is_success = False

            # 校驗
            google_auth_key = AppCache().get_chain_google_auth_key(AppCache().get_login_chain())
            if not pyotp.TOTP(google_auth_key).verify(args.verify_code):
                Logger().logger.error("google authentication fail")

                return Exceptions.ERR_GOOGLE_AUTH
            
            is_success = True
            AppCache().set_google_auth()
            return Exceptions.ERR_OK
        
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            
            return Exceptions.ERR_SERVER
            
        finally:
            # 寫入操作表
            operate_log = TableAgentOperateLog()
            operate_log.login_time = int(time.time())
            operate_log.wallet_address = AppCache().get_login_wallet_address() or ''
            operate_log.error_type = OperateErrType.OT_GOOGLE_AUTH_SUCCESS if is_success else OperateErrType.OT_GOOGLE_AUTH_FAIL

            SQLiteDB().insert(TableAgentOperateLog._table_name, operate_log.to_dict())

        
