
# -*- coding:utf-8 -*-

class AppCache():
    # 單列模式
    _instance = None
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance
    
    def init(self, private_key : str, public_key : str, config : dict = None):
        self._config = config
        self._private_key = private_key
        self._public_key = public_key
        
        self._token = None
        self._login_network = None
        self._login_wallet_address = None
        self._is_google_auth = False
    
    def config_update(self, config : dict):
        self._config = config

    def reinit(self):
        self._token = None
        self._login_network = None
        self._login_wallet_address = None
        self._is_google_auth = False

    def get_private_key(self):
        return self._private_key
    
    def get_public_key(self):
        return self._public_key

    def get_network_contract_address(self, network : str):
        return self._config.get('address', {}).get(network, {}).get('contract_address', '')
    
    def get_network_wallet_address(self, network : str):
        return self._config.get('address', {}).get(network, {}).get('wallet_address', [])
    
    def get_network_list(self):
        return self._config.get('address', {}).keys()
    
    def get_network_list_include_chainid(self):
        data_list = []
        for k, v in self._config.get('address', {}).items():
            data_list.append({'network':k, 'chainid':v.get('chainid','')})
        
        return data_list
    
    def get_network_google_auth_key(self, network : str):
        return self._config.get('address', {}).get(network, {}).get('google_auth_key', [])
    
    def set_token(self, token : str):
        self._token = token
    
    def get_token(self):
        return self._token
    
    def set_login_wallet_address(self, wallet_address : str):
        self._login_wallet_address = wallet_address

    def get_login_wallet_address(self):
        return self._login_wallet_address
        
    def set_login_network(self, network):
        self._login_network = network
    
    def get_login_network(self):
        return self._login_network
        
    def set_google_auth(self):
        self._is_google_auth = True

    def get_google_auth(self):
        return self._is_google_auth
    
