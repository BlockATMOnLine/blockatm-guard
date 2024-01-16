# -*- coding:utf-8 -*-
import traceback
import yaml
import os
from typing import List
from pydantic import BaseModel, Field
from core.exceptions import Exceptions
from utils.cache import AppCache
from utils.logger import Logger

class APIInit():
        
    # 回覆參數
    class RespondArgs(BaseModel):
        
        class Data(BaseModel):
            class NetWorkChain(BaseModel):
                network : str = Field(examples=['Ethereum', 'Tron'],description='網絡')
                chainid : str = Field(examples=['5', '0'],description='chainid')
                contract_address : str = Field(examples=['0x3e27ade2c81415e781'], description='合約地址')
                wallet_address : list = Field(examples=[['0xe9fa4f143f073fd501', '0xE618a1aB24B7869']], description='錢包地址')

            version : str = Field(examples=['3.1.4'],description='chainid')
            network_list : List[NetWorkChain] = Field(description='網絡列表')
            public_key : str = Field(examples=["ODJIDIJDJIJLDH"],description = '公鑰')

        ret : int = Field(examples=[0],description = '返回結果：0-成功，非0-失敗')
        msg : str = Field(examples=['success'],description = '應答結果描述')
        data : Data = None

    @staticmethod
    def handle_request():
        try:
            
            network_list = []
            for k, v in AppCache().get_chain_info().items():
                network_chain = APIInit.RespondArgs.Data.NetWorkChain(network = v['network'], 
                                                                      chainid = k, 
                                                                      contract_address = v['contract_address'],
                                                                      wallet_address = v['wallet_address'])
                network_list.append(network_chain)
            
            public_key = AppCache().get_public_key()
            data = APIInit.RespondArgs.Data(version=AppCache().get_front_version(),network_list=network_list, public_key=public_key)
            return Exceptions.ERR_OK, data.model_dump()

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return Exceptions.ERR_SERVER
            


