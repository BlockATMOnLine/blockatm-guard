# -*- coding:utf-8 -*-
import os
import sqlite3
import traceback
import platform
from db.sqlcrypt import Connection
from core.config import DB_PASSWORD, VERSION_TYPE
from core.setting import VersionType
from typing import Union
from utils.logger import Logger
from utils.tool import OSName, get_run_dir

# 加密數據庫名稱
encrypt_db_name = 'agentapp_encrypt.db'
decrypt_db_name = 'agentapp_decrypt.db'
# sqlcipher_shell_exe = 'sqlcipher-shell64.exe'

class SQLiteDB():

    def __init__(self, secret_key : str = DB_PASSWORD):
        self._secret_key = secret_key
        self._db_name = encrypt_db_name

    def execute(self, sql : str):
        dbfile = os.path.join(get_run_dir(), self._db_name)
        Logger().logger.info(f'dbfile = {dbfile}')

        conn = Connection(dbfile, self._secret_key)
        cur = conn.execute(sql)
        res = cur.fetchall()
        conn.close()
        return res

    # 查詢
    def query_sql(self, sql : str):
        try:
            Logger().logger.info(f'sql = {sql}')
            if platform.system() == OSName.OS_WINDOWS:
                return self.execute(sql)
            else:
                return self.execute(sql)
        
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

            if sql[-1] != ";":
                sql += ';'

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

            sql = f'''insert into {table}({field_str}) values ({vaule_str});'''
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
        
    # 删除
    def delete_sql(self, sql : str):
        try:
            Logger().logger.info(f'sql = {sql}')
            return self.execute(sql)

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return False
    
    # 删除
    def delete(self, table : str, filter : Union[list, dict]):
        try:
            filter_str = '1 = 1 '
            
            if isinstance(filter, dict):
                for k, v in filter.items():
                    if isinstance(v, str):
                        filter_str += f' and {k} = \'{v}\''
                    else:
                        filter_str += f' and {k} = {v}'

            elif isinstance(filter, list):
                for f in filter:
                    filter_str += f' and {f}'

            sql = f'delete from {table} where {filter_str}'

            return self.delete_sql(sql)
        
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return False

    



