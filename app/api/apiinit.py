# -*- coding:utf-8 -*-
import traceback
from typing import List, Dict
from pydantic import BaseModel, Field
from core.exceptions import Exceptions
from db.sqlitedb import SQLiteDB
from utils.cache import AppCache
from utils.logger import Logger

class APIInit():
        
    # 回覆參數
    class RespondArgs(BaseModel):
        
        class Data(BaseModel):
            class NetWorkChain(BaseModel):
                network : str = Field(examples=['Ethereum', 'Tron'],description='網絡')
                chainid : str = Field(examples=['5', '0'],description='chainid')

            network_list : List[NetWorkChain] = Field(description='網絡列表')
            public_key : str = Field(examples=["ODJIDIJDJIJLDH"],description = '公钥')

        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')
        data : Data = None

    @staticmethod
    def handle_request():
        try:
            
            network_list = []
            for item in AppCache().get_network_list_include_chainid():
                network_chain = APIInit.RespondArgs.Data.NetWorkChain(network = item['network'], chainid = item['chainid'])
                network_list.append(network_chain)
            
            public_key = AppCache().get_public_key()
            data = APIInit.RespondArgs.Data(network_list=network_list, public_key=public_key)
            return Exceptions.ERR_OK, data.model_dump()

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return Exceptions.ERR_SERVER
            


