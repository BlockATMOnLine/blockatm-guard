# BlockATM-Guard

## 簡介

BlockATM-Guard 是一款用python開發的桌面端虛擬貨幣代付系統

## 搭建環境

### Python環境

python > 3.9

```
# windows
python3 -m pip install -r requirements_windows.txt
```

```
# mac
python3 -m pip install -r requirements_mac.txt
```

### 建庫

```
python3 alembic/initdb.py -e agentapp_encrypt.db -d agentapp_decrypt.db -p 123456
```

生成sqlite本地db文件：加密的數據庫 agentapp_encrypt.db 和 沒有加密數據庫 agentapp_decrypt.db 

### 配置

修改 ./core/config.py 內容

```
# 版本類型: DEBUG, RELEASE
# DEBUG: 使用 agentapp_decrypt.db 非加密db, 輸出詳細日誌
# RELEASE: 使用 agentapp_encrypt.db 加密db, 不輸出敏感信息日誌
VERSION_TYPE = 'DEBUG'

# 數據庫密碼
# RELEASE 模式下有效
DB_PASSWORD = '123456'
```

### 啟動程序

```
python3 app/main.py
```



