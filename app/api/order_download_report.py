# -*- coding:utf-8 -*-
import os
import traceback
import pandas
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from utils.logger import Logger
from db.sqlitedb import SQLiteDB
from db.table import TableAgentHistoryOrder
from core.exceptions import Exceptions
from core.setting import REPORT_EXCEL_FILE_NAME, REPORT_EXCEL_SAVE_FOLDER
from utils.cache import AppCache
from utils.tool import timestamp_to_datetime_str, get_run_dir

class APIOrderDownloadReport():

    @staticmethod
    def handle_request(time_start : int, time_end : int, order_no : str, crypto : str, network : str, amount_start : str, amount_end : str, uid : str, biz_name : str, wallet_address : str):
        try:

            sql = f'''select * from {TableAgentHistoryOrder._table_name} where 1 = 1 '''
            if time_start:
                sql += f' and order_date >= {time_start} '
            
            if time_end:
                sql += f' and order_date =< {time_end} '

            if order_no:
                sql += f' and order_no = \'{order_no}\''
            
            if crypto:
                sql += f' and crypto = \'{crypto}\''
            
            if network:
                sql += f' and network = \'{network}\''
            
            if amount_start:
                sql += f' and cast(amount as decimal(18,12)) >= {amount_start}'
            
            if amount_end:
                sql += f' and cast(amount as decimal(18,12)) <= {amount_end}'
            
            if uid:
                sql += f' and uid = \'{uid}\''
            
            if biz_name:
                sql += f' and biz_name = \'{biz_name}\''
            
            if wallet_address:
                sql += f' and wallet_address = \'{wallet_address}\''
            
            sql += ' order by finish_date desc'

            res_list = SQLiteDB().query_sql(sql)
            
            Logger().logger.error(f'order_list = {res_list}')

            # 校驗數據結果
            if not isinstance(res_list, list):
                return Exceptions.ERR_DB

            # 訂單數據
            execel_data = {"Date of Order":[], "Business":[], "Order No.":[], "TxID":[], "UID":[], "Amount":[],
                           "Token":[], "Wallet Address":[], "Service Fee":[], "Date of Payment":[], "Status":[]}
            for db_res in res_list:
                table_order = TableAgentHistoryOrder()
                table_order.assignment(db_res)

                # network篩選
                if table_order.network != AppCache().get_login_network():
                    continue

                execel_data['Date of Order'].append(timestamp_to_datetime_str(table_order.order_date, '%d-%m/%Y %H:%M'))
                execel_data['Business'].append(table_order.biz_name)
                execel_data['Order No.'].append(table_order.order_no)
                execel_data['TxID'].append(table_order.txid)
                execel_data['UID'].append(table_order.uid)
                execel_data['Amount'].append(table_order.amount)
                execel_data['Token'].append(table_order.crypto)
                execel_data['Wallet Address'].append(table_order.wallet_address)
                execel_data['Service Fee'].append(1)
                execel_data['Date of Payment'].append(timestamp_to_datetime_str(table_order.finish_date, '%d-%m/%Y %H:%M'))
                execel_data['Status'].append('Success')
            
            Logger().logger.debug(f'execel_data = {execel_data}')
            df = pandas.DataFrame(execel_data, columns = execel_data.keys())

            Logger().logger.debug(f'df = {df}')
            
            # 創建目錄
            dir = f"{get_run_dir()}/{REPORT_EXCEL_SAVE_FOLDER}"
            if(os.path.exists(dir) == False):
                os.makedirs(dir)

            file_path = f'{dir}/{REPORT_EXCEL_FILE_NAME}'
            df.to_excel(file_path, sheet_name='Orders', index = False)

            return FileResponse(path=file_path, filename=REPORT_EXCEL_FILE_NAME)

        except Exception as err:
            Logger().logger.error('{} :{}'.format(err, str(traceback.format_exc())))

            return Exceptions.ERR_SERVER
