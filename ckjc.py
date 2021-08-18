#!/bin/env python3
# -*- coding: utf-8 -*

from urllib.parse import unquote, quote
import time, datetime, os, sys
import requests, json, re, random
import threading

UserAgent = ''
script_name = 'CK失效检测'

def printT(msg):
    print("[{}]: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
    sys.stdout.flush()

def delEnvs(label):
    try:
        if label == 'True' or label == 'yes' or label == 'true' or label == 'Yes':
            return True
        elif label == 'False' or label == 'no' or label == 'false' or label == 'No':
            return False
    except:
        pass
    try:
        if '.' in label:
            return float(label)
        elif '&' in label:
            return label.split('&')
        elif '@' in label:
            return label.split('@')
        else:
            return int(label)
    except:
        return label


class getJDCookie():
    # 适配青龙平台环境ck
    def getckfile(self):
        ql_new = '/ql/config/env.sh'
        ql_old = '/ql/config/cookie.sh'
        if os.path.exists(ql_new):
            printT("当前环境青龙面板新版")
            return ql_new
        elif os.path.exists(ql_old):
            printT("当前环境青龙面板旧版")
            return ql_old

    # 获取cookie
    def getallCookie(self):
        cookies = ''
        ckfile = self.getckfile()
        try:
            if os.path.exists(ckfile):
                with open(ckfile, "r", encoding="utf-8") as f:
                    cks_text = f.read()
                if 'pt_key=' in cks_text and 'pt_pin=' in cks_text:
                    r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
                    cks_list = r.findall(cks_text)
                    if len(cks_list) > 0:
                        for ck in cks_list:
                            cookies += ck
            return cookies
        except Exception as e:
            printT(f"【getCookie Error】{e}")

    # 检测cookie格式是否正确
    def getUserInfo(self, ck, user_order, pinName):
        url = 'https://me-api.jd.com/user_new/info/GetJDUserInfoUnion?orgFlag=JD_PinGou_New&callSource=mainorder&channel=4&isHomewhite=0&sceneval=2&sceneval=2&callback='
        headers = {
            'Cookie': ck,
            'Accept': '*/*',
            'Connection': 'close',
            'Referer': 'https://home.m.jd.com/myJd/home.action',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'me-api.jd.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'zh-cn'
        }
        try:
            resp = requests.get(url=url, headers=headers, timeout=60).json()
            if resp['retcode'] == "0":
                pass
            else:
                context = f"账号{user_order}【{pinName}】Cookie 已失效！请重新获取。"
                print(context)
                return ck, False
        except Exception:
            context = f"账号{user_order}【{pinName}】Cookie 已失效！请重新获取。"
            print(context)
            return ck, False

    def getcookies(self):
        """
        :return: cookiesList,userNameList,pinNameList
        """
        cookies = self.getallCookie()
        if 'pt_key=' in cookies and 'pt_pin=' in cookies:
            r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
            result = r.findall(cookies)
            if len(result) >= 1:
                printT("您已配置{}个账号".format(len(result)))
                user_order = 1
                for ck in result:
                    r = re.compile(r"pt_pin=(.*?);")
                    pinName = r.findall(ck)
                    pinName = unquote(pinName[0])
                    # ck检测
                    self.getUserInfo(ck, user_order, pinName)

        else:
            printT("没有可用Cookie，已退出")
            exit(4)

# 随机UA
def userAgent():
    """
    随机生成一个UA
    :return: jdapp;iPhone;9.4.8;14.3;xxxx;network/wifi;ADID/201EDE7F-5111-49E8-9F0D-CCF9677CD6FE;supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone13,4;addressid/2455696156;supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1
    """
    if not UserAgent:
        uuid = ''.join(random.sample('123456789abcdef123456789abcdef123456789abcdef123456789abcdef', 40))
        addressid = ''.join(random.sample('1234567898647', 10))
        iosVer = ''.join(
            random.sample(["14.5.1", "14.4", "14.3", "14.2", "14.1", "14.0.1", "13.7", "13.1.2", "13.1.1"], 1))
        iosV = iosVer.replace('.', '_')
        iPhone = ''.join(random.sample(["8", "9", "10", "11", "12", "13"], 1))
        ADID = ''.join(random.sample('0987654321ABCDEF', 8)) + '-' + ''.join(
            random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(
            random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 12))

        return f'jdapp;iPhone;10.0.4;{iosVer};{uuid};network/wifi;ADID/{ADID};supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone{iPhone},1;addressid/{addressid};supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS {iosV} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'
    else:
        return UserAgent

# 设置请求头
def setHeaders(cookie):
    headers = {
        "Host": "api.m.jd.com",
        "cookie": cookie,
        "charset": "UTF-8",
        "accept-encoding": "br,gzip,deflate",
        "user-agent": "okhttp/3.12.1;jdmall;android;version/10.0.8;build/89053;screen/1080x2029;os/10;network/wifi;",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset\u003dUTF-8",
        "content-length": "48"
    }
    return headers

def start():
    printT("############{}##########".format(script_name))
    get_jd_cookie = getJDCookie()
    get_jd_cookie.getcookies()

if __name__ == '__main__':
    start()









