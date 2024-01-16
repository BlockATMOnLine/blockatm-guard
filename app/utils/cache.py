
# -*- coding:utf-8 -*-

class AppCache():
    # 單列模式
    _instance = None
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance
    
    def init(self, private_key : str, public_key : str, config : dict, front_version : str, network_info:dict):
        self._config = config
        self._front_version = front_version
        self._network_info = network_info

        self._private_key = private_key
        self._public_key = public_key
        
        self._token = None
        self._login_chainid = None
        self._login_wallet_address = None
        self._is_google_auth = False
    
    def config_update(self, config : dict):
        self._config = config

    def reinit(self):
        self._token = None
        self._login_chainid = None
        self._login_wallet_address = None
        self._is_google_auth = False

    def get_private_key(self):
        return self._private_key
    
    def get_public_key(self):
        return self._public_key

    def get_front_version(self):
        return self._front_version

    def get_chain_contract_address(self, chainid : str):
        return self._config.get('address', {}).get(chainid, {}).get('contract_address', '')
    
    def get_chain_wallet_address(self, chainid : str):
        return self._config.get('address', {}).get(chainid, {}).get('wallet_address', [])
    
    def get_chain_network(self, chainid):
        return self._config.get('address', {}).get(chainid, {}).get('network', [])
    # def get_network_list(self):
    #     return self._config.get('address', {}).keys()
    
    def get_chain_list(self):
        return self._config.get('address', {}).keys()
    
    def get_chain_info(self)->dict:
        return self._config.get('address', {})
    
    def get_chain_google_auth_key(self, chainid : str):
        return self._config.get('address', {}).get(chainid, {}).get('google_auth_key', [])
    
    def set_token(self, token : str):
        self._token = token
    
    def get_token(self):
        return self._token
    
    def set_login_wallet_address(self, wallet_address : str):
        self._login_wallet_address = wallet_address

    def get_login_wallet_address(self):
        return self._login_wallet_address
        
    def set_login_chain(self, chainid):
        self._login_chainid = chainid
    
    def get_login_chain(self):
        return self._login_chainid
        
    def set_google_auth(self):
        self._is_google_auth = True

    def get_google_auth(self):
        return self._is_google_auth
    
    # {'5': {'network':'Ethereum Goerli'}}
    def get_info_by_network(self, network : str):

        for k, v in self._network_info.items():
            if v.get('network') == network:
                return k, v.get('regular')
        
        return False, False