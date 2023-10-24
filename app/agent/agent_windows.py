import os
import requests
import datetime
from utils.logger import Logger
from utils.tool import check_free_port
from PyQt5 import QtGui, QtCore, QtNetwork    # pip3 install PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem     # pip install PyQtWebEngine
from PyQt5.QtCore import pyqtSignal, QObject
from core.setting import REPORT_EXCEL_FILE_NAME
from PyQt5.QtCore import QTimer

class Signals(QObject):
    url_signal = pyqtSignal(str)

signals = Signals()

class AgentMainWindow(QMainWindow,):
    def __init__(self, host : str, port : int):
        super(AgentMainWindow, self).__init__()

        self.timer = QTimer()
        self.timer.timeout.connect(self.set_url)
        self.timer.start(200)

        self._host = host
        self._port = port
        self._url = f'http://{host}:{port}/index.html'

        self.setWindowTitle('BlockATM-Guard')
        self.resize(1400, 750)
        
        self.setWindowIcon(QtGui.QIcon('./resource/favicon.png'))
        self.browser = AppWebEngineView()
        
        url = f'http://{host}:{port}/index.html'
        #url = f'http://{host}:{port}/v1/agent/order/download_order_template?isTrusted=true&_vts=169767959437'
        #self.browser.setUrl(QtCore.QUrl(url))

        #self.manager = QtNetwork.QNetworkAccessManager()

        self.setCentralWidget(self.browser)

        # 接收信號
        signals.url_signal.connect(self.set_url)
    
    def set_url(self):
        if check_free_port(self._port):
            Logger().logger.info('set url')
            self.timer.stop()
            self.browser.setUrl(QtCore.QUrl(self._url))
    
    def closeEvent(self, event : QtGui.QCloseEvent):
        
        reply = QMessageBox.warning(self, 'Exit', 'Confirm to exit?', QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Ok:
            Logger().logger.info('push logout!')
            
            # 推送登出
            url = f'http://{self._host}:{self._port}/v1/agent/logout'
            # 本地禁用代理
            proxies = {
                "http": "",
                "https": "",
            }
            respond = requests.post(url, proxies=proxies)
            Logger().logger.info(f'logout respond = {respond.text}')
            
            event.accept()
        else:
            event.ignore()

class AppWebEngineView(QWebEngineView):

    def __init__(self, parent=None):
        super(AppWebEngineView, self).__init__(parent)
    
        self.page().profile().downloadRequested.connect(self.on_downloadRequested) #頁面下載請求

    # 支持頁面下載按鈕
    def on_downloadRequested(self, qtdownloadItem : QWebEngineDownloadItem):
        save_file_path= QFileDialog.getSaveFileName(None, 'Save Report', f'{os.getcwd()}/{REPORT_EXCEL_FILE_NAME}')

        Logger().logger.info(f'select path = {save_file_path}')

        # 没有选择目录直接返回
        if not save_file_path[0]:
            QMessageBox.warning(self, 'Cancel', 'Download Canceled!', QMessageBox.StandardButton.Ok)
            return

        if not qtdownloadItem.isFinished() and qtdownloadItem.state() == 0:
            
            ###下载文件
            # qtdownloadItem.setSavePageFormat(QWebEngineDownloadItem.CompleteHtmlSaveFormat)
            qtdownloadItem.setPath(save_file_path[0])
            qtdownloadItem.accept()
            qtdownloadItem.finished.connect(self.on_downloadfinished)

    # 下载结束触发函数
    def on_downloadfinished(self):
        QMessageBox.information(self, 'Success', 'Download Success!', QMessageBox.StandardButton.Ok)