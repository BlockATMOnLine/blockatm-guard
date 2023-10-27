# BlockATM Guard

<p>
<a href="https://www.gnu.org/licenses/gpl-3.0.html"><img src="https://img.shields.io/badge/license-GPLV3-blue" alt="license GPLV3"></a>
<a href="https://github.com/assimon/dujiaoka/releases/tag/1.0.0"><img src="https://img.shields.io/badge/version-1.0.0-red" alt="version 1.0.0"></a>
</p>
<h2 align="center">繁體中文 | <a href="README_EN.md">English</a></h2>

## BlockATM Guard - 行業創新的`區塊鏈`安全支付解決方案

> BlockATM Guard是PassTo旗下`BlockATM`产品系列中的开源Desktop DApp。為BlockATM的商業客戶提供安全可靠的`代收代付`功能，業内首創自主打包的`開源客戶端`，`無密鑰存儲`，提高資金安全水平。

## 相關產品 -- BlockATM-智能合約收付款解決方案

> 完全去中心化的商戶收付款方式  
> 使用智能合約進行資金的安全管理  
> 使用費率比fireBlocks和metaMask都低  
> [點擊創建你的智能合約櫃檯](https://www.blockatm.net/)

## 推薦產品 -- PassTo-多種資產抵押信用卡

> 無上限信用額 單筆消費可達$5,000,000  
> 信用額度按照抵押品價格而設定，支持：證券、物業、貴金屬、數字資產等  
> 可绑微信、支付宝、美区AppStore消费  
> [點擊領取你的國際信用卡](https://passtocredit.io/)

## 產品特點

- `智能合約`：使用智能合約進行加密貨幣的收付，安全可靠，鏈上资金流动可实时记录，确保資金数据的准确性和透明性。支持多種穩定幣，比如：`ERC USDT`、`ERC DAI`、`TRC USDT`等

- `財務管理`：支持多种财务操作，包括转账、收款、付款和结算等。并且可以自定义设置支付条件和限额，确保安全性和合规性。

- `極簡部署`：提供智能合约交互界面。用户可以轻松创建和执行智能合约，实现更复杂的财务操作和自动化流程。

- `隱私安全`：用户可以设置多重身份验证、MFA、UKEY、WEB3账户识别等安全校驗，使用RSA证书加密技术和HTTPS安全通信协议，並提供本地异常记录机制，實時監控異常場景

- `可擴展性`：提供完善的三方對接功能，收銀檯和API都支持商戶對接

- `BlockATM Guard` 遵守 [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html) 開源協議


## 項目結構

```
project
├── alembic                  # 数据库迁移相关脚本
│   ├── [env.py](http://env.py/)
│   ├── README
│   ├── script.py.mako
│   └── versions            # 迁移版本目录
│       └── xxxxxxxx_yy_zzzzzzzzzzzz.py
├── app                     # 项目主目录
│   ├── api                 # API 控制器目录
│   │   ├── **init**.py
│   │   └── [example.py](http://example.py/)
│   ├── config              # 项目配置目录
│   │   ├── **init**.py
│   │   ├── [dev.py](http://dev.py/)          # 开发环境配置
│   │   └── [prod.py](http://prod.py/)         # 生产环境配置
│   ├── core                # 项目核心目录
│   │   ├── **init**.py
│   │   ├── [config.py](http://config.py/)       # 通用配置加载器
│   │   ├── [exceptions.py](http://exceptions.py/)   # 异常处理器
│   │   └── [settings.py](http://settings.py/)     # 项目设置
│   ├── db                  # 数据库相关目录
│   │   ├── **init**.py
│   │   ├── [base.py](http://base.py/)         # 数据库模型基类
│   │   ├── [crud.py](http://crud.py/)         # 数据库操作工具
│   │   ├── [session.py](http://session.py/)      # 数据库会话相关
│   │   └── models          # 数据库模型目录
│   │       ├── **init**.py
│   │       └── [example.py](http://example.py/)
│   ├── [main.py](http://main.py/)             # 主程序入口
│   ├── schemas             # 数据验证和输入输出格式化目录
│   │   ├── **init**.py
│   │   └── [example.py](http://example.py/)
│   └── utils               # 工具函数目录
│       ├── **init**.py
│       ├── [cache.py](http://cache.py/)        # 缓存工具
│       ├── [logging.py](http://logging.py/)      # 日志工具
│       └── [response.py](http://response.py/)     # HTTP 响应工具
├── tests                   # 单元测试目录
│   ├── **init**.py
│   ├── test_example.py
│   └── [conftest.py](http://conftest.py/)
├── .env                    # 环境变量配置文件
├── .gitignore
├── .dockerignore
├── .docker-compose.yml
├── Dockerfile              # Docker 构建文件
├── requirements.txt        # 项目依赖清单
└── [README.md](http://readme.md/)
```

### 部署操作説明

#### Python環境

python > 3.9

```
# windows
python3 -m pip install -r requirements_windows.txt
```

```
# mac
python3 -m pip install -r requirements_mac.txt
```

#### 建庫

```
python3 alembic/initdb.py -e agentapp_encrypt.db -d agentapp_decrypt.db -p 123456
```

生成sqlite本地db文件：加密的數據庫 agentapp_encrypt.db 和 沒有加密數據庫 agentapp_decrypt.db

#### 配置

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

#### 啟動程序

```
cd app
python3 main.py
```

## 加入交流/意見反饋

- Telegram：https://t.me/PayCool_Erik
- Email：erik.wang@chixi88.com

## 頁面截圖
![][link_cashier] ![][link_success]

[link_cashier]: image/cashier.png
[link_success]: image/success.png
