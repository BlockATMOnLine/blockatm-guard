# -*- coding:utf-8 -*-
class Language():
    languages = ["en-US", "zh-HK", "zh-CN"]
    LANG_ENGLISH = languages[0]         # 英文
    LANG_TRADITIONAL = languages[1]     # 繁體
    LANG_CHINESE = languages[2]         # 中文

class Exceptions():
    class ExValue():
        def __init__(self, values : list) -> None:
            if len(values) != 4:
                raise ValueError("values len must be 4")
            if not isinstance(values[0], int):
                raise ValueError("values[0] must be int type")

            self._values = values

        def get_code(self):
            return self._values[0]
        
        def get_desc(self, language = Language.LANG_ENGLISH):
            if language not in Language.languages:
                language = Language.LANG_ENGLISH
            return self._values[Language.languages.index(language) + 1]
        
    ERR_OK = ExValue([0, 'Success', '成功', '成功'])
    ERR_NETWORK_NOT_SUPPORT = ExValue([301, 'Network not supported, please switch', '此網路不支緩, 請切換', '此钱包地址不支持'])
    ERR_WALLET_ADDRESS_NOT_SUPPORT = ExValue([302, 'Wallet address not supported', '此錢包地址不支援', "此钱包地址不支持"])
    ERR_MAC_NOT_SUPPORT = ExValue([303, 'MAC address not supported', '此mac地址不支援', '此mac地址不支持'])
    ERR_DB = ExValue([312, 'DB execution error, please try agian later', 'DB執行錯誤, 請稍後再試', 'DB执行错误, 请稍后再试'])
    ERR_SERVER = ExValue([313, 'Internal server error, please try agian later', '服務器內部錯誤, 請稍後再試', '服务器内部错误, 请稍后再试'])
    ERR_GOOGLE_AUTH = ExValue([314, 'Google authentication failed, please try again.', 'Google驗證失敗, 請重試', 'Google验证失败, 请重试']) 
    ERR_CONTRACT_ADDRESS_NULL = ExValue([315, 'Contract address does not exist', '合約地址不存在', '合约地址不存在'])
    ERR_UPLOAD_ORDER_NO_EXIST = ExValue([316, 'The uploaded order(s) number already exists. Please double-check and re-upload the orders. ', 
                                 ' 上傳訂單號已經存在, 請檢查後重新上傳', '上传订单号已 经存在, 请检查后重新上传'])
    ERR_UPLOAD_NETWORK_NO_MATCH = ExValue([317, 'The uploaded order(s) does not match the network. Please switch network and upload it again.', 
                                   '上傳訂單有與網絡不匹配的, 請轉換路網後再上傳', '上 传订单有与网络不匹配的，请切换网络后再上传'])
    ERR_UPLOAD_VALUES_HAVE_CHAR = ExValue([318, "The uploaded data contains the '|' character. Please remove it and upload again.", 
                                   "上傳資料包含 '|' 字元, 請移除後重新上傳", "上传资料包含 '|' 字 符, 请移除后重新上传"])
    ERR_NOT_VERIFY_GOOGLE_AUTH = ExValue([320, 'Please verify with Google Authenticator before proceeding with the upload.', 
                                  '上傳前請先以Google驗證器驗證', '上传前请先以Google验证器验证'])        
    ERR_READ_EXCEL_ERROR = ExValue([321, 'The attempt to read the Excel file has encountered a failure.', '讀取 Excel 檔案失敗', '读取 Excle 文件失败'])

    

    