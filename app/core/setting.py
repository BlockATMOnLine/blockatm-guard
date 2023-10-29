
class VersionType():
    VT_DEBUG = 'DEBUG'
    VT_RELEASE = 'RELEASE'

class NetWorkType():
    NWT_ETH = 'Ethereum'
    NWT_TRON = 'Tron'

class NetWorkRegular():
    NWR_ETH = '^0x[0-9a-fA-F]{40}$'
    NWR_TRON = '^T[1-9A-HJ-NP-Za-km-z]{33}$'

REPORT_EXCEL_SAVE_FOLDER = 'report'
REPORT_EXCEL_FILE_NAME = 'blockatm_gurad_report.xlsx'