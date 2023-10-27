import time
from typing import Callable
import webbrowser

from db.sqlitedb import SQLiteDB
from db.table import TableAgentLoginLog
from utils.logger import Logger
from utils.cache import AppCache
from utils.tool import get_run_dir
from utils.crypto_engine import RASEngine
from core.exceptions import Exceptions, Language
from core.config import VERSION_TYPE
from core.setting import VersionType
from agent.agent_config import LOGGING_CONFIG

import uvicorn
from fastapi import Depends, FastAPI, Header, Body, UploadFile, File, Form, HTTPException, Response
from fastapi.routing import APIRoute
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
from api.apiinit import APIInit
from api.config_update import APIConfigUpdate
from api.login import APILogin
from api.logout import APILogout
from api.order_delete import APIOrderDelete
from api.order_history import APIOrderHistory
from api.order_pay_fail import APIOrderPayFail
from api.order_pay_success import APIOrderPaySuccess
from api.order_pay_lock import APIOrderPayLock
from api.order_query_wait import APIOrderQueryWait
from api.order_pay_winding import APIOrderPayWinding
from api.order_upload import APIOrderUpload
from api.order_download_template import APIOrderDownloadTemplate
from api.order_download_report import APIOrderDownloadReport
from api.log_login import APIQueryLoginLog
from api.log_operate import APIQueryOperateLog
from api.verify_google_auth import APIVerifyGoogleAuth

# 定義解密 route
class CryptoRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:

            Logger().logger.info("custom_route_handler")
            Logger().logger.info(f"url = {request.url}")

            if request.method == 'POST' and not hasattr(request, "_body") and request.url.path not in ['/v1/agent/order/upload_order_file']:
                body = await request.body()
                if body:
                    
                    Logger().logger.info(f"body = {body}")
                    # 解密
                    body = body.decode()
                    decrypt_data = ""
                    for elem in body.split(','):
                        decrypt_data += RASEngine.rasdecrypt(AppCache().get_private_key(), elem)
                    request._body = decrypt_data.encode()

            return await original_route_handler(request)

        return custom_route_handler


class AgentServer():

    def run(self, host : str, port : int, config : dict, process_token : str):
        # 初始化日誌
        if VERSION_TYPE == VersionType.VT_RELEASE:
            Logger().init('blockatm-guard', f'{get_run_dir()}/logs', level='info')
        else:
            Logger().init('blockatm-guard', f'{get_run_dir()}/logs', level='debug')

        Logger().logger.debug(f'run config = {config}')

        self._private_key, self._public_key = RASEngine.create_rsa_key()
        self._host = host
        self._port = port
        self._process_toke = process_token
        AppCache().init(self._private_key, self._public_key, config)

        Logger().logger.debug(f'private_key = {self._private_key}')
        Logger().logger.debug(f'public_key = {self._public_key}')
        
        if VERSION_TYPE == VersionType.VT_RELEASE:
            self._app = FastAPI(title = 'Agnet WebServer', description = 'Agnet WebServer 接口文檔', version='v1.0.0')
        else:
            self._app = FastAPI(title = 'Agnet WebServer', description = 'Agnet WebServer 接口文檔', version='v1.0.0')
        
        Logger().logger.info(f'get_run_dir = {get_run_dir()}')
        self._app.mount("/static", StaticFiles(directory=f"{get_run_dir()}/static"), name="static")
        self._templates = Jinja2Templates(directory=f"{get_run_dir()}/templates")
        self._app.router.route_class = CryptoRoute

        # api定義
        self.api_define(self._app)

        # 啟動服務
        if VERSION_TYPE == VersionType.VT_RELEASE:
            uvicorn.run(self._app, host = host, port = port, log_config=None)
        else:
            uvicorn.run(self._app, host = host, port = port, log_config=None)
            #uvicorn.run(self._app, host = host, port = port)
    
    # header驗證
    def verify_header(self, token : str = Header(), lang : str = Header()):
        if AppCache().get_token() != token:
            raise HTTPException(status_code=400, detail="token header invalid")
        
        if lang not in Language.languages:
            raise HTTPException(status_code=400, detail="lang header invalid")
    
    def verify_process_token(self, process_token : str = Header()):
        if self._process_toke != process_token:
            raise HTTPException(status_code=400, detail="process token header invalid")
    
    # 統一回復
    def respond(self, api_respond, language : str = Language.LANG_ENGLISH):
        ret = {}
        if isinstance(api_respond, tuple):
            ex_value : Exceptions.ExValue = api_respond[0]
            data = api_respond[1]
            ret = {'ret': ex_value.get_code(), 'msg' : ex_value.get_desc(language), 'data' : data}
        else:
            ex_value = api_respond
            ret = {'ret': ex_value.get_code(), 'msg' : ex_value.get_desc(language)}
        
        Logger().logger.debug(f'ret = {ret}')
        return ret
    
    # api定義
    def api_define(self, app : FastAPI):
        # 啟動事件
        @app.on_event("startup")
        async def startup_event():
            Logger().logger.info("start uvicorn service")

            url = f'http://{self._host}:{self._port}/?apiKey=03AB7BAF-3E9C-4A54-9CE6-55741A8C98C8'

            Logger().logger.info(f'url = {url}')
            #signals.url_signal.emit(url)

        # 停止事件
        @app.on_event("shutdown")
        async def shutdown_event():
            Logger().logger.info("close uvicorn service")

            if AppCache().get_token():
                SQLiteDB().update(TableAgentLoginLog._table_name, {'token':AppCache().get_token()}, {'logout_time':int(time.time())})

        # 主頁
        @app.get("/index.html", tags=['主頁'], summary='主頁')
        def index(request: Request):
            return self._templates.TemplateResponse("index.html", {"request": request})
        
        # 配置
        @app.get("/v1/agent/config_update", tags=['配置'], response_model = APIConfigUpdate.RespondArgs, summary='更新配置')
        def config_update(config : str):
            return self.respond(APIConfigUpdate.handle_request(config))
        
        # 登錄
        @app.post('/v1/agent/login', tags=['登錄'], response_model = APILogin.RespondArgs, summary='登錄')
        def login(lang : str = Header(), args : APILogin.RequestArgs = Body()):
            return self.respond(APILogin.handle_request(args), lang)
        
        # 登出
        @app.post('/v1/agent/logout', tags=['登錄'], response_model = APILogout.RespondArgs, summary='登出')
        def logout():
            return self.respond(APILogout.handle_request())
        
        # 初始化
        @app.get('/v1/agent/config', tags=['初始化'], response_model = APIInit.RespondArgs, summary='初始化')
        def config():
            return self.respond(APIInit.handle_request())
        
        # 刪除訂單
        @app.post('/v1/agent/order/delete', dependencies=[Depends(self.verify_header)], tags=['訂單'], response_model = APIOrderDelete.RespondArgs, summary='刪除訂單')
        def query_history_order(lang : str = Header(), args : APIOrderDelete.RequestArgs = Body()):
            return self.respond(APIOrderDelete.handle_request(args), lang)
        
        # 歷史訂單
        @app.post('/v1/agent/order/history', dependencies=[Depends(self.verify_header)], tags=['訂單'], response_model = APIOrderHistory.RespondArgs, summary='查詢歷史訂單')
        def query_history_order(lang : str = Header(), args : APIOrderHistory.RequestArgs = Body()):
            return self.respond(APIOrderHistory.handle_request(args), lang)
        
        # 訂單支付失敗
        @app.post('/v1/agent/order/pay_fail', dependencies=[Depends(self.verify_header)], tags=['訂單'], response_model = APIOrderPayFail.RespondArgs, summary='訂單支付失敗')
        def query_history_order(lang : str = Header(), args : APIOrderPayFail.RequestArgs = Body()):
            return self.respond(APIOrderPayFail.handle_request(args), lang)
        
        # 訂單支付成功
        @app.post('/v1/agent/order/pay_success', dependencies=[Depends(self.verify_header)], tags=['訂單'], response_model = APIOrderPaySuccess.RespondArgs, summary='訂單支付成功')
        def query_history_order(lang : str = Header(), args : APIOrderPaySuccess.RequestArgs = Body()):
            return self.respond(APIOrderPaySuccess.handle_request(args), lang)
        
        # 訂單上鍊
        @app.post('/v1/agent/order/pay_winding', dependencies=[Depends(self.verify_header)], tags=['訂單'], response_model = APIOrderPayWinding.RespondArgs, summary='訂單上鍊')
        def query_history_order(lang : str = Header(), args : APIOrderPayWinding.RequestArgs = Body()):
            return self.respond(APIOrderPayWinding.handle_request(args), lang)
        
        # 訂單鎖定
        @app.post('/v1/agent/order/pay_lock', dependencies=[Depends(self.verify_header)], tags=['訂單'], response_model = APIOrderPayLock.RespondArgs, summary='訂單鎖定')
        def query_history_order(lang : str = Header(), args : APIOrderPayLock.RequestArgs = Body()):
            return self.respond(APIOrderPayLock.handle_request(args), lang)
        
        # 查詢待支付訂單
        @app.get('/v1/agent/order/query_wait', dependencies=[Depends(self.verify_header)], tags=['訂單'], response_model = APIOrderQueryWait.RespondArgs, summary='查詢待支付訂單')
        def query_history_order(lang : str = Header()):
            return self.respond(APIOrderQueryWait.handle_request(), lang)
        
        # 導入訂單excel文件
        @app.post("/v1/agent/order/upload_order_file", tags=['訂單'], response_model = APIOrderUpload.RespondArgs, summary='導入訂單excel文件')
        def upload_payout_order_file(lang : str = Header(), file: UploadFile = File(...), file_password : str = Form(...)):
            return self.respond(APIOrderUpload.handle_request(file, file_password), lang)
        
        # 下載訂單模板
        @app.get(f"/v1/agent/order/download_order_template", tags=['訂單'], summary='下載訂單模板')
        def order_download_template():
            return APIOrderDownloadTemplate.handle_request()
        
        # 下載報表
        @app.get("/v1/agent/order/download_order_report", tags=['訂單'], summary='下載訂單報表')
        def order_download_report(time_start : int, time_end : int, payment_start:int, payment_end:int, order_no : str, crypto : str, network : str, amount_start : str, amount_end : str, uid : str, biz_name : str, wallet_address : str):
            return APIOrderDownloadReport.handle_request(time_start, time_end, payment_start, payment_end, order_no, crypto, network, amount_start, amount_end, uid, biz_name, wallet_address)
        
        # 查詢登錄日誌
        @app.get("/v1/agent/log/login_log", dependencies=[Depends(self.verify_header)], tags=['日誌'], response_model = APIQueryLoginLog.RespondArgs, summary='查詢登錄日誌')
        def query_log(lang : str = Header()):
            return self.respond(APIQueryLoginLog.handle_request(), lang)
        
        # 查詢操作日誌
        @app.get("/v1/agent/log/operate_log", dependencies=[Depends(self.verify_header)], tags=['日誌'], response_model = APIQueryOperateLog.RespondArgs, summary='查詢操作日誌')
        def query_log(lang : str = Header()):
            return self.respond(APIQueryOperateLog.handle_request(), lang)
        
        # 谷歌auth驗證
        @app.post("/v1/agent/verify/google_auth", dependencies=[Depends(self.verify_header)], tags=['驗證'], response_model = APIVerifyGoogleAuth.RespondArgs, summary='谷歌auth驗證')
        def verify_google_auth(lang : str = Header(), args : APIVerifyGoogleAuth.RequestArgs = Body()):
            return self.respond(APIVerifyGoogleAuth.handle_request(args), lang)
        
        # 打開本地瀏覽器
        @app.post("/v1/agent/local/open_webbrowser", tags=['本地'], summary='打開本地瀏覽器')
        def open_webbrowser(lang : str = Header(), url: str = Body(..., description="鏈接", embed=True)):
            Logger().logger.info(f'url = {url}')
            webbrowser.open(url)
            return self.respond(Exceptions.ERR_OK, lang)
        