# -*- coding:utf-8 -*-
import os
import sqlite3
import traceback
import platform
from core.config import DB_PASSWORD, VERSION_TYPE
from core.setting import VersionType
from typing import Union
from utils.logger import Logger
from utils.tool import OSName, get_run_dir
from subprocess import Popen, PIPE

# 加密數據庫名稱
encrypt_db_name = 'agentapp_encrypt.db'
decrypt_db_name = 'agentapp_decrypt.db'
sqlcipher_shell_exe = 'sqlcipher-shell64.exe'

class SQLiteDB():

    def __init__(self, secret_key : str = DB_PASSWORD):
        self._secret_key = secret_key
        if VERSION_TYPE == VersionType.VT_RELEASE and platform.system() == OSName.OS_WINDOWS:
            self._db_name = encrypt_db_name
        else:
            self._db_name = decrypt_db_name

    def execute_macos(self, sql):
        dbfile = os.path.join(get_run_dir(), self._db_name)
        Logger().logger.info(f'dbfile = {dbfile}')
        conn = sqlite3.connect(dbfile)
        return conn.execute(sql)
            
    def execute_windwos(self, sql):
        try:
            #exe_cmd = "%s %s" % (get_exe_file(), self._db_name)
            exe_cmd = "%s %s" % (sqlcipher_shell_exe, self._db_name)
            p1 = Popen(exe_cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)

            if VERSION_TYPE == VersionType.VT_RELEASE:
                cmd_sql = f"PRAGMA key = '{self._secret_key}';{sql};"
            else:
                cmd_sql = f"{sql};"

            code, message = p1.communicate(bytes(cmd_sql, encoding='utf-8'))
            message = message.decode("gbk")
            Logger().logger.debug(f"code = {code}, message = {message}")
            if int(p1.poll()) == 0:
                res = code.decode('utf-8')
                res = res.strip('\r\n')
                res = [_ for _ in res.split('\r\n') if _]
                res = [_.split('|') for _ in res]
                Logger().logger.info(f"sql execute success")
                Logger().logger.debug(f"res = {res}")
                return res
            else:
                Logger().logger.error(f"sql execute fail")
            
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

    def execute(self, sql : str):
        if platform.system() == OSName.OS_WINDOWS:
            return self.execute_windwos(sql)
        else:
            return self.execute_macos(sql)

    # 查詢
    def query_sql(self, sql : str):
        try:
            
            Logger().logger.info(f'sql = {sql}')
            if platform.system() == OSName.OS_WINDOWS:
                return self.execute(sql)
            else:
                return self.execute(sql).fetchall()
        
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
    
    # 查詢
    def query(self, table : str, filter : Union[list, dict] = None, fields : list = [], sort_field : list = [], desc = False):
        try: 
            field_str = ','.join(fields)
            filter_str = '1 = 1 '

            # dict賦值
            if isinstance(filter, dict):
                for k, v in filter.items():
                    if isinstance(v, str):
                        filter_str += f' and {k} = \'{v}\''
                    else:
                        filter_str += f' and {k} = {v}'

            # list對接
            elif isinstance(filter, list):
                for f in filter:
                    filter_str += f' and {f}'

            if fields:
                sql = f'''select {field_str} from {table} where {filter_str}'''
            else:
                sql = f'''select * from {table} where {filter_str}'''
            
            # 排序
            if sort_field:
                sort_field_str = ','.join(sort_field)
                sql += f' order by {sort_field_str}'

                # 升序降序
                if desc:
                    sql += ' desc'

            return self.query_sql(sql)
        
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return False
    
    # 插入
    def insert_sql(self, sql : str):
        try:
            Logger().logger.info(f'sql = {sql}')

            return self.execute(sql)
        
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return False

    # 插入
    def insert(self, table : str, field_vaules : dict):
        try:
            field_str = ','.join(field_vaules.keys())
            vaule_str = ''
            for v in field_vaules.values():
                if isinstance(v, str):
                    vaule_str += f'\'{v}\','
                else:
                    vaule_str += f'{v},'
            if vaule_str:
                vaule_str = vaule_str[:-1]

            sql = f'''insert into {table}({field_str}) values ({vaule_str})'''
            #Logger().logger.info(f'sql = {sql}')
            return self.insert_sql(sql)

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

    # 更新
    def update_sql(self, sql : str):
        try:
            Logger().logger.debug(f'sql = {sql}')
            return self.execute(sql)

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return False
    
    # 更新
    def update(self, table : str, filter : dict, field_vaules : dict = None):
        try:
            field_vaule_str = ''
            filter_str = '1 = 1 '

            for k, v in field_vaules.items():
                if isinstance(v, str):
                    field_vaule_str += f'{k} = \'{v}\','
                else:
                    field_vaule_str += f'{k} = {v},'
            
            if field_vaule_str:
                field_vaule_str = field_vaule_str[:-1]

            for k, v in filter.items():
                if isinstance(v, str):
                    filter_str += f' and {k} = \'{v}\''
                else:
                    filter_str += f' and {k} = {v}'

            
            #Logger().logger.info(f'sql = {sql}')
            sql = f'''update {table} set {field_vaule_str} where {filter_str}'''

            return self.update_sql(sql)

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return False
        



    



