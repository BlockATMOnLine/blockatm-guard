
import copy
from utils.logger import Logger

class TableBase():
    # 獲取 fields
    def get_fields(self)->list:
        return self.__class__.__dict__['__annotations__'].keys()

    # 字段轉成dict
    def to_dict(self, filter_fields : list = []):
        # 拷貝
        object_data : dict = copy.deepcopy(self.__dict__)
        class_data : dict = copy.deepcopy(self.__class__.__dict__['__annotations__'])
        
        # 過濾
        [object_data.pop(_) for _ in filter_fields if _ in object_data.keys()]
        [class_data.pop(_) for _ in filter_fields if _ in class_data.keys()]

        # 校驗keys
        if object_data.keys() != class_data.keys():
            Logger().logger.error(f'object_data key = {object_data.keys()}')
            Logger().logger.error(f'class_data key = {class_data.keys()}')
            Logger().logger.error('keys not match, missing some parameters')
            return
        
        # 校驗數據類型
        for k, v in class_data.items():
            if not isinstance(object_data[k], v):
                Logger().logger.error(f'key = {k}, data = {object_data[k]}, type = {v}, data type not match, ')
                return
        
        return object_data
    
    # 賦值
    def assignment(self, dbdata : tuple):
        field_dict : dict = self.__class__.__dict__['__annotations__']

        i = 0
        for field, type in field_dict.items():
            self.__dict__[field] = type(dbdata[i])
            i += 1
        
        return self

# 配置表
class TableAgentConfig(TableBase):
    _table_name = 'agent_config'

    yaml_file : str = None
    config : str = None
    update_time : int = None
    aes_key : str = None

# 操作日誌表
class TableAgentOperateLog(TableBase):
    _table_name = 'agent_operate_log'

    # 字段按照建表順序
    login_time : int = None
    wallet_address : str = None
    error_type : str = None

# 登錄日誌表
class TableAgentLoginLog(TableBase):
    _table_name = 'agent_login_log'
    
    # 字段按照建表順序
    token : str = None
    login_time : int =  None
    logout_time : int =  None
    wallet_address : str =  None
    mac : str = None

# 訂單表
class TableAgentOrder(TableBase):
    _table_name = 'agent_order'

    # 字段按照建表順序
    order_no : str = None
    order_date : int = None
    import_date : int = None
    crypto : str = None
    network : str = None
    wallet_address : str = None
    amount : str = None
    uid : str = None
    biz_name : str = None
    status : int = None                 # 訂單狀態: 0-未支付, 1-鎖定, 2-上鍊, 3-完成, 4-超時
    txid : str = None                   # 上鍊後會傳txid
    is_del : int = None                 # 是否刪除: 0-未刪除，1-刪除

# 成功支付訂單表
class TableAgentHistoryOrder(TableBase):
    _table_name = 'agent_history_order'

    order_no : str = None
    order_date : int = None
    import_date : int = None
    finish_date : int = None
    crypto : str = None
    network : str = None
    wallet_address : str = None
    amount : str = None
    uid : str = None
    biz_name : str = None

