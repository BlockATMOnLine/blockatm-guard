# -*- coding:utf-8 -*-
import os
import sys
import argparse
import sqlite3
import traceback
from pypi_sqlite_cipher.pysqlite_cipher import encryption_sqlite_file

def create_db(encrypt_dbname : str, decrypt_dbname : str, password : str):
    try:

        # 連接db
        conn = sqlite3.connect(decrypt_dbname)

        # 建表
        conn.execute('''CREATE TABLE agent_order
                    (
                    order_no VARCHAR(128) PRIMARY KEY,
                    order_date INTEGER   NOT NULL,
                    import_date INTEGER   NOT NULL,
                    crypto VARCHAR(64)   NOT NULL,
                    network VARCHAR(128) NOT NULL,
                    wallet_address VARCHAR(128) NOT NULL,
                    amount VARCHAR(64)  NOT NULL,
                    uid VARCHAR(128) NOT NULL,
                    biz_name VARCHAR(128) NOT NULL,
                    status INTEGER NOT NULL,
                    txid VARCHAR(128),
                    is_del INTEGER
                    );''')
        
        conn.execute('''CREATE TABLE agent_history_order
                    (
                    order_no VARCHAR(128) PRIMARY KEY,
                    order_date INTEGER   NOT NULL,
                    import_date INTEGER   NOT NULL,
                    finish_date INTEGER   NOT NULL,
                    crypto VARCHAR(64)   NOT NULL,
                    network VARCHAR(128) NOT NULL,
                    wallet_address VARCHAR(128) NOT NULL,
                    amount VARCHAR(64)  NOT NULL,
                    uid VARCHAR(128) NOT NULL,
                    biz_name VARCHAR(128) NOT NULL,
                    txid VARCHAR(128)  NOT NULL
                    );''')

        conn.execute('''CREATE TABLE agent_login_log
                    (
                    token VARCHAR(128) PRIMARY KEY,
                    login_time INTEGER NOT NULL,
                    logout_time INTEGER NOT NULL,
                    wallet_address VARCHAR(128)    NOT NULL,
                    mac VARCHAR(128)   NOT NULL
                    );''')

        conn.execute('''CREATE TABLE agent_operate_log
                    (
                    login_time INTEGER NOT NULL,
                    wallet_address VARCHAR(128)   NOT NULL,
                    error_type VARCHAR(256) NOT NULL
                    );''')

        conn.execute('''CREATE TABLE agent_config
                    (
                    yaml_file VARCHAR(256) NOT NULL,
                    config JSON NOT NULL,
                    update_time int NOT NULL,
                    aes_key VARCHAR(256) NOT NULL
                    );''')

        conn.close()

        # 加密數據庫
        res = encryption_sqlite_file(decrypt_dbname, password)

        print(res)

        if res[0] == 'success':
            os.rename('encrypted.db', encrypt_dbname)
            return True
        else:
            return False

    except Exception as err:
        print('{} :{} '.format(err, str(traceback.format_exc())))

    finally:
        #os.remove(temp_dbname)
        pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-e", "--encrypt_dbname", required=True, help="加密db")
    parser.add_argument("-d", "--decrypt_dbname", required=True, help="非加密db")
    parser.add_argument("-p", "--password", required=True, help="password")

    known_args = parser.parse_args()

    sys.exit(create_db(known_args.encrypt_dbname, known_args.decrypt_dbname, known_args.password))