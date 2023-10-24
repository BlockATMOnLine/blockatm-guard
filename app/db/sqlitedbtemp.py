# -*- coding:utf-8 -*-
import sqlite3
import traceback
from typing import Optional, List, Dict, Union
from utils.logger import Logger

global_db_name = 'agentapp_encrypt.db'

class SQLiteDB():

    # # 單列模式
    # _instance = None
    # def __new__(cls, *args, **kw):
    #     if cls._instance is None:
    #         cls._instance = object.__new__(cls, *args, **kw)
    #     return cls._instance

    def __init__(self, name : str = global_db_name, password : str = None):
        self._conn = sqlite3.connect(name)
    
    def __del__(self):
        if self._conn:
            self._conn.close()
    
    # 查詢
    def query_sql(self, sql : str):
        try:
            
            Logger().logger.info(f'sql = {sql}')

            return self._conn.execute(sql).fetchall()
        
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
    
    # 查詢
    def query(self, table : str, filter : Union[list, dict] = None, fields : list = []):
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
            
            #Logger().logger.info(f'sql = {sql}')

            return self.query_sql(sql)
        
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return False
    
    # 插入
    def insert_sql(self, sql : str):
        try:
            Logger().logger.info(f'sql = {sql}')
            self._conn.execute(sql)
            self._conn.commit()

            return True
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
            Logger().logger.info(f'sql = {sql}')
            self._conn.execute(sql)
            self._conn.commit()
            return True
        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))
            return False
    
    # 更新
    def update(self, table : str, filter : dict, field_vaules : dict):
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
        



    



