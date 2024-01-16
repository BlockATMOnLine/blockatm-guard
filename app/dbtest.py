from db.sqlitedb import SQLiteDB
from db.table import TableAgentConfig
from utils.logger import Logger


Logger().init('test', './logs', level='info')

res = SQLiteDB().query(TableAgentConfig._table_name)
Logger().logger.info(res)

# res = SQLiteDB().update(TableAgentConfig._table_name, {}, {'config':'{"version":1697889631677,"address":{"5":{"contract_address":"0x3e27ade2c81415e781b5797c4a0ab13782047823","network":"Ethereum","wallet_address":["0xe9fa4f143f073fd5017daa03b5863bb3966dcce4","0xE618a1aB24B786970AA4BAED33aBF9ec7694B547"],"google_auth_key":"WUZYEKZWDODIFUU3"},"0x94a9059e":{"contract_address":"TAcoDwjqw5M4QUZUgzwKQxt7hgo1kUhcUm","network":"Tron","wallet_address":["TUsCQhcJCrSFKSaAtPXQtyk1SKpVxSVyC4"],"google_auth_key":"WUZYEKZWDODIFUU399"}}}'})
# Logger().logger.info(res)

# res = SQLiteDB().query(TableAgentConfig._table_name)
# Logger().logger.info(res)