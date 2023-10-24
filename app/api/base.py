# -*- coding:utf-8 -*-
class OrderDel():
    VALUES = [0, 1]

    OD_NOT_DEL = VALUES[0]
    OD_DEL = VALUES[1]

class OrderStatus():
    VALUES = [0, 1, 2, 3, 4]

    OS_NOT_PROCESS = VALUES[0]  # 未處理
    OS_LOCK = VALUES[1]         # 鎖定
    OS_WINDING = VALUES[2]      # 上鍊
    OS_FINISH = VALUES[3]       # 完成
    OS_TIMEOUT = VALUES[4]      # 超時

class OperateErrType():
    OT_LOGIN_FAIL = 'Login Fail!'
    OT_LOGIN_SUCCESS = 'Login Success!'
    OT_ORDER_PAY = 'Order Pay!'
    OT_LOGIN_MAC_INCORRECT = 'Mac Address Incorrect!'
    OT_LOGIN_WALLET_ADDRESS_INCORRECT = 'Wallet Address Incorrect!'
    OT_GOOGLE_AUTH_FAIL = 'Google Authentication Fail!'
    OT_GOOGLE_AUTH_SUCCESS = 'Google Authentication Success!'

