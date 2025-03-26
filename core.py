import socket
import requests
import time
import os
import random
from logger import logger

Status = dict(
    running=True,
    ipv4='',
    ipv6=''
)


# def get_time_str():
#     return time.strftime("%Y-%m-%d %H:%M:%S")


def random_dic(dicts):
    dict_key_ls = list(dicts.keys())
    random.shuffle(dict_key_ls)
    new_dict = {}
    for key in dict_key_ls:
        new_dict[key] = dicts.get(key)
    return new_dict


class ConfigError(Exception):
    def __init__(self, message="配置文件错误"):
        self.message = message
        super().__init__(self.message)


def get_ip(mode='local', urls=None):
    '''
    获取局域网/公网ip
    :param mode: local==局域网，public==公网，auto==公网/局域网/127.0.0.1
    :return:
    '''
    if urls is None:
        urls = {
            'http://jsonip.com': 'ip',  # 支持ipv4/6
            'http://6.ipw.cn': None,  # ipv6
            # 'http://api6.ipify.org': None,  # ipv6
            'https://ipv6onlyapi.wcode.net/openapi/ipv6onlyapi/client-ip#': "data.client_ip",  # ipv6
            # 'https://api.ipify.org/?format=json': 'ip',  # 支持ipv4
            # 'http://httpbin.org/ip': 'origin'
        }
    urls = random_dic(urls)
    if mode == 'local':
        status = False
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            status = True
        except:
            ip = '127.0.0.1'
    elif mode == 'public':
        ip = None
        status = False
        for url in urls:
            try:
                os.environ['NO_PROXY'] = url
                res = requests.request('get', url, verify=False, timeout=10)
                if urls[url]:  # 返回json对象，需要根据key取值
                    keys = urls[url].split('.')
                    ip = res.json()
                    for key in keys:
                        ip = ip[key]
                    # ip = res.json()[urls[url]]
                else:  # 返回结果就是ip地址
                    ip = res.text
                logger.logger.info(f'Get ipv6 from {url}')
                status = True
                break
            except Exception as e:
                logger.logger.error(f"Failed to get public ip from {url}： {e}")
                status = False
        if ip is None:
            ip = '127.0.0.1'
    else:
        status = False
        ip = '127.0.0.1'
    if not status:
        logger.logger.info('网络异常，获取ip失败！')
    return status, ip


def update_ipv4(domain, token):
    try:
        status, ipv4 = get_ip('local')
        if not status:
            return
        logger.logger.info(f'IPv4: {ipv4}')
        url_v4 = f'http://dynv6.com/api/update?hostname={domain}&token={token}&ipv4={ipv4}'
        res4 = requests.request('get', url_v4)
        logger.logger.info(f'IPv4 update: {res4.text}')
    except Exception as e:
        logger.logger.error(f'Network exception: {e}')
        return

    # 网络正常，但是配置文件错误
    if 'invalid authentication token' in res4.text:
        # logger.logger.error(f"Please check whether the configuration file is correct. INFO: {res4.text}")
        raise ConfigError(f"Please check whether the configuration file is correct. INFO: {res4.text}")
    else:
        Status['ipv4'] = ipv4

def update_ipv6(domain, token, mask=128, urls=None):
    try:
        status, ipv6 = get_ip('public', urls)
        if not status:
            return
        logger.logger.info(f'IPv6: {ipv6}')
        url_v6 = f'http://dynv6.com/api/update?hostname={domain}&ipv6={ipv6}/{mask}&token={token}'
        res6 = requests.request('get', url_v6)
        logger.logger.info(f'IPv6 update: {res6.text}')
    except Exception as e:
        logger.logger.error(f'Network exception: {e}')
        return

    # 网络正常，但是配置文件错误
    if 'invalid authentication token' in res6.text:
        # logger.logger.error(f"Please check whether the configuration file is correct. INFO: {res6.text}")
        raise ConfigError(f"Please check whether the configuration file is correct. INFO: {res6.text}")
    else:
        Status['ipv6'] = ipv6

def update_dynv6(domain, token, mask=128, urls=None):
    # logger.logger.info(f'[{get_time_str()}]')

    update_ipv4(domain, token)
    update_ipv6(domain, token, mask, urls)


if __name__ == '__main__':
    mode = 'once'  # once：运行一次；interval：每隔一段时间运行一次
    # mode = 'interval'  # once：运行一次；interval：每隔一段时间运行一次
    interval_seconds = 5
    domain = 'host.dynv6.net'
    token = 'Benutzername for Your Domain'
    mask = 128
    while True:
        update_dynv6(domain, token, mask)  # cmd查看python进程：tasklist | findstr "python"
        if mode == 'interval':
            time.sleep(interval_seconds)
        else:
            break
