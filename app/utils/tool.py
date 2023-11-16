# -*- coding:utf-8 -*-
import time
import datetime
import uuid
import os
import platform
import sys
from decimal import Decimal

class OSName():
    OS_WINDOWS = "Windows"
    OS_MAC = "Darwin"
    OS_LINUX = "Linux"
    OS_OTHER = "Other"

def get_work_dir():
    os_name = platform.system()
    if os_name == OSName.OS_WINDOWS:
        return '.'
    
    return os.path.join(os.path.expanduser('~'), 'blockatm-guard')

def get_run_dir():
    os_name = platform.system()
    if os_name == OSName.OS_WINDOWS:
        return '.'
    
    executable_file = sys.executable
    if 'python' in os.path.basename(executable_file):
        return '.'
    
    #return os.path.dirname(sys.argv[0]).rsplit('/', 3)[0]
    return os.path.abspath(os.path.dirname(__file__).rsplit('/', 1)[0])
    #return os.path.dirname(sys.executable).rsplit('/', 3)[0]
    #return os.path.dirname(executable_file)
    #return os.path.join(os.path.dirname(sys.executable), "../../..")

def get_mac_address():
    """
    獲取本機物理地址，獲取本機mac地址
    :return:
    """
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:].upper()
    return "-".join([mac[e:e+2] for e in range(0,11,2)])

def check_free_port(port):
    """
    檢測ip端口是否空閒
    """
    os_name = platform.system()
    #print(f'current os = {os_name}')
    if os_name == OSName.OS_WINDOWS:
        cmd = f'netstat -aon|findstr "{port}"'
    elif os_name == OSName.OS_MAC:
        cmd = f'lsof -i :{port}'
    else:
        raise Exception("not support this os system!")
    
    res = os.popen(cmd).read()
    if res:
        return True
    
    return False

def get_free_port(default_port = 5500):
    """
    獲取空閒的端口
    """
    port = None
    for i in range(default_port, 65535):
        if not check_free_port(i):
            port = i
            break

    return port

def datetime_str_to_second_timestamp(date, format="%Y-%m-%d"):
    """
    時間字符串轉秒級時間戳
    """
    # 先轉換為時間數組
    timeArray = time.strptime(date, format)
    # 轉換為時間戳
    return int(time.mktime(timeArray))

def datetime_object_to_second_timestamp(date : datetime.datetime):
    """
    時間對象轉秒級時間戳
    """
    # 轉換為時間戳
    return int(time.mktime(date.timetuple()))

def timestamp_to_datetime_str(timestamp, format = "%d-%m/%Y %H:%M"):
    """
    時間戳轉格式字符串
    """

    return time.strftime(format, time.localtime(timestamp))

def check_amount(value : str):
    """
    檢測金額是否為整形或者浮點型
    """
    try:
        Decimal(value)
        return True
    except Exception:
        return False

def compare_version(version1 : str, version2 : str)->int:
    """
    版本比較
    return: 0-相同, 1-version1大, -1-version1小
    """
    if version1 == version2:
        return 0
    
    v1 = version1.split('.')
    v2 = version2.split('.')

    # 取最小長度
    lent = len(v1) if len(v1) < len(v2) else len(v2)

    for i in range(0, lent):
        if int(v1[i]) == int(v2[i]):
            continue
        elif int(v1[i]) > int(v2[i]):
            return 1
        else:
            return -1
    
    