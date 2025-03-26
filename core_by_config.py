from core import update_dynv6, ConfigError, Status
import time
import json
from logger import logger
import os
import traceback

# ConfFile = os.path.abspath('./dynv6_for_dev.conf')
ConfFile = os.path.abspath('./dynv6.conf')

Config = dict(
    urls={
        'http://jsonip.com': 'ip',  # url: 结果解析字段
        'http://6.ipw.cn': None,  # 结果解析字段为None时，直接返回请求返回的文本
        "https://ipv6onlyapi.wcode.net/openapi/ipv6onlyapi/client-ip#": "data.client_ip"
    },
    domain="host.dynv6.net",
    token="Benutzername for Your Domain",
    mask=128,
    mode="interval",
    seconds=600,
    # log="./dynv6_for_dev.log"
    log="./dynv6.log"
)

class JsonFileOps:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def write(self, info):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=4)

    def read(self) -> dict:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data

def set_conf_file(config=Config):
    json_op = JsonFileOps(ConfFile)
    json_op.write(config)

def load_conf_file():
    if os.path.exists(ConfFile):
        json_op = JsonFileOps(ConfFile)
        return json_op.read()
    else:
        return Config

def dynv6_updater():
    json_op = JsonFileOps(ConfFile)
    # 创建or加载配置文件
    if not os.path.exists(ConfFile):
        json_op.write(Config)
        logger.start(Config['log'])
        logger.logger.info(f'The configuration file has been initialized to "{ConfFile}" successfully. '
                           'Please complete the configuration information and then restart the software.')
        return 'Config Initialized'
    else:
        try:
            conf = json_op.read()
            logger.start(conf.get('log', Config['log']))
        except Exception as e:
            logger.start(Config['log'])
            logger.logger.error(str(e))
            logger.logger.error(traceback.format_exc())
            return
    # 根据配置文件信息更新DDNS
    urls = conf['urls']
    domain = conf['domain']
    token = conf['token']
    mask = conf['mask']
    mode = conf['mode']
    seconds = conf['seconds']

    # 更新ip
    logger.logger.info('Dynv6 updater has started!')
    logger.logger.info(f'Mode: {mode}')
    logger.logger.info(f'Seconds: {seconds}')
    try:
        while True:
            update_dynv6(domain, token, mask, urls)  # cmd查看python进程：tasklist | findstr "python"
            if mode == 'interval':
                for _ in range(seconds):
                    if Status['running']:
                        time.sleep(1)
                    else:
                        logger.logger.info('Dynv6 updater has stopped!')
                        return
            else:
                break
    except ConfigError as e:
        logger.logger.error(f"Config error: {e}")
        return 'Config Error'
    except Exception as e:
        logger.logger.error(f'Update ip error: {e}')

if __name__ == '__main__':
    dynv6_updater()
