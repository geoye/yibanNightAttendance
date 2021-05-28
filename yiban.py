# -*- coding: utf-8 -*-
import requests
import json
import re
import time
import os

# 代码部分参考自https://hub.fastgit.org/rookiesmile/yibanAutoSgin
class yiban:
    CSRF = "64b5c616dc98779ee59733e63de00dd5"
    COOKIES = {"csrf_token": CSRF}
    HEADERS = {"Origin": "https://c.uyiban.com", "User-Agent": "yiban_iOS/4.9.4"}
    
    def __init__(self, mobile, password):
        self.mobile = mobile
        self.password = password
        self.session = requests.session()
        # 从https://lbs.amap.com/tools/picker 寻找宿舍经纬度
        LNGLAT=os.environ["LNGLAT"]
        ADDRESS=os.environ["ADDRESS"]
        self.night_sgin ='{"Reason":"","AttachmentFileName":"","LngLat":%s,"Address":%s}' %(LNGLAT,ADDRESS)
        
    def login(self):
        params = {
            "mobile": self.mobile,
            "password": self.password,
            "imei": "0",
        }
        # 登录接口
        response = self.request("https://mobile.yiban.cn/api/v3/passport/login", params=params, cookies=self.COOKIES)
        if response is not None and response["response"] == 100:
            self.access_token = response["data"]["user"]["access_token"]
            return response
        else:
            return response
        
    def auth(self) -> json:
        location = self.session.get("http://f.yiban.cn/iapp/index?act=iapp7463&v=" + self.access_token,
                                    allow_redirects=False).headers["Location"]
        verifyRequest = re.findall(r"verify_request=(.*?)&", location)[0]
        response = self.request(
            "https://api.uyiban.com/base/c/auth/yiban?verifyRequest=" + verifyRequest + "&CSRF=" + self.CSRF,
            cookies=self.COOKIES)
        return response
        
    def request(self, url, method="get", params=None, cookies=None):
        if method == "get":
            response = self.session.get(url=url, timeout=10, headers=self.HEADERS, params=params, cookies=cookies)
        elif method == "post":
            response = self.session.post(url=url, timeout=10, headers=self.HEADERS, data=params, cookies=cookies)

        return response.json()


    def deviceState(self):
        return self.request(url="https://api.uyiban.com/nightAttendance/student/index/deviceState?CSRF=" + self.CSRF,
                            cookies=self.COOKIES)

    def sginPostion(self):
        return self.request(url="https://api.uyiban.com/nightAttendance/student/index/signPosition?CSRF=" + self.CSRF,
                            cookies=self.COOKIES)
    
    def nightAttendance(self, info) -> json:
        params = {
            "Code": "",
            "PhoneModel": "",
            "SignInfo": info,
            "OutState": "1"
        }
        response = self.request("https://api.uyiban.com/nightAttendance/student/index/signIn?CSRF=" + self.CSRF,
                                method="post", params=params, cookies=self.COOKIES)
        return response
        
    def setall(self):
        self.login()
        self.auth()
        # self.deviceState() 实际签到时不需要
        time.sleep(1)
        self.sginPostion()
        time.sleep(1)
        status = self.nightAttendance(self.night_sgin)
        return status

def main():
    # 修改下方的手机号和密码，即可实现一个宿舍一起签到
    MOBILE=os.environ["MOBILE"]
    PASSWORD=os.environ["PASSWORD"]
    a = yiban(MOBILE, PASSWORD)
#    b = yiban("moblie", "password")
#    c = yiban("moblie", "password")
#    d = yiban("moblie", "password")
    yb_list = [a]
    for i in range(len(yb_list)):
        status = yb_list[i].setall()
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print(status)
        time.sleep(1)
    
if __name__ == '__main__':
    main()
    
