
# @author:HUI
# @time:2020-10-30


# 阳光体育晨跑

import datetime
from random import randint, uniform

import requests


def encrypt(number):
    key = "xfvdmyirsg"
    #key = "ahgfkjzyxy"
    numbers = list(map(int, list(str(number))))
    return_key = "".join([key[i] for i in numbers])
    return return_key


class Aipaoer(object):
    # 初始化
    def __init__(self, IMEICode):
        self.IMEICode = IMEICode
        # token
        self.Token = ''
        # 软件内ID
        self.UserID = ''
        # 姓名
        self.NickName = ''
        # 学号
        self.UserName = ''
        # 性别
        self.Sex = ''
        # 学校名称
        self.SchoolName = ''
        # 学校ID
        self.SchoolId = ''
        # RunID
        self.RunID = ''
        # MinSpeed
        self.MinSpeed = ''
        # MaxSpeed
        self.MaxSpeed = ''
        # Lengths
        self.Lengths = ''
        # 晨跑次数
        self.RaceMNums = 0
        # 总跑步次数
        self.RaceNums = 0
        # 跑步记录
        self.record_list = []

    def __str__(self):
        return str(self.__dict__).replace("\'", "\"")

    # 检查imei有效性并载入Token
    def imei_check(self):
        url = "http://client3.aipao.me/api/%7Btoken%7D/QM_Users/Login_AndroidSchool?IMEICode={IMEICode}".format(
            IMEICode=self.IMEICode)
        # headers = {'version': '2.40'}
        headers = {'version': '2.44','Host': 'client3.aipao.me','Connection': 'Keep-Alive'}
        # 返回响应
        rsp = requests.get(url, headers=headers)
        # Json解码
        rsp_json = rsp.json()
        # print(rsp_json)
        # 异常处理
        try:
            if rsp_json["Success"]:
                self.Token = rsp_json['Data']['Token']
                self.UserID = rsp_json['Data']['UserId']
                self.get_all_info()
                return True
            else:
                return False
        # KeyError 字典中查询一个不存在
        except KeyError:
            # print("imei失效")
            return False

    # 获取用户信息
    def get_info(self):
        url = "http://client3.aipao.me/api/{Token}/QM_Users/GS".format(
            Token=self.Token)
        #headers = {'version': '2.40'}
        headers = {'version': '2.44', 'Host': 'client3.aipao.me', 'Connection': 'Keep-Alive'}
        rsp = requests.get(url, headers=headers)
        rsp_json = rsp.json()
        # print(rsp_json)
        try:
            self.UserName = rsp_json["Data"]["User"]["UserName"]
            self.NickName = rsp_json["Data"]["User"]["NickName"]
            self.SchoolName = rsp_json["Data"]["SchoolRun"]["SchoolName"]
            self.MinSpeed = rsp_json["Data"]["SchoolRun"]["MinSpeed"]
            self.MaxSpeed = rsp_json["Data"]["SchoolRun"]["MaxSpeed"]
            self.Lengths = rsp_json["Data"]["SchoolRun"]["Lengths"]
        except KeyError:
            print("Unknown error in get_info")

    # 开始跑步获取RunId
    def get_RunId(self):
        url = "http://client3.aipao.me/api/{Token}/QM_Runs/SRS?S1=32.35011&S2=119.40146&S3={Lengths}".format(
            Token=self.Token, Lengths=self.Lengths)
        #headers = {'version': '2.40'}
        headers = {'version': '2.44', 'Host': 'client3.aipao.me', 'Connection': 'Keep-Alive'}
        rsp = requests.get(url, headers=headers)
        try:
            self.RunID = rsp.json()["Data"]["RunId"]
        except KeyError:
            print("Unknown error in get_runId")

    # 上传跑步信息
    def upload(self):
        # 跑步必备信息Get
        # self.get_info()
        # self.get_RunId()
        lengths = int(self.Lengths) + randint(0, 1)
        steps = randint(950, 1250)
        speed = round(uniform(float(self.MinSpeed) + 0.3, float(self.MaxSpeed) - 1.5), 2)
        cost_time = int(lengths // speed)
        params = {
            "Token": self.Token,
            "RunID": self.RunID,
            "cost_time": encrypt(cost_time),
            "lengths": encrypt(lengths),
            "steps": encrypt(steps)}
        url = "http://client3.aipao.me/api/{Token}/QM_Runs/ES?" \
              "S1={RunID}&S4={cost_time}&S5={lengths}&S6=B4B1B0B4B3&S7=1&S8=xfvdmyirsg&S9={steps}".format(**params)
        #headers = {'version': '2.40'}
        headers = {'version': '2.44', 'Host': 'client3.aipao.me', 'Connection': 'Keep-Alive'}
        rsp = requests.get(url, headers=headers)
        try:
            if rsp.json()["Success"]:
                return True
        except KeyError:
            fin = {'msg': 'error'}
            return False

    # 跑步数据查询
    def download(self):
        url = "http://client3.aipao.me/api/{Token}/QM_Runs/getResultsofValidByUser" \
              "?UserId={UserId}&pageIndex=1&pageSize=10".format(Token=self.Token, UserId=self.UserID)
        #headers = {'version': '2.40'}
        # headers = {'version': '2.44', 'Host': 'client3.aipao.me', 'Connection': 'Keep-Alive'}
        headers = {'version': '2.44', 'Host': 'client3.aipao.me', 'Connection': 'Keep-Alive'}

        rsp = requests.get(url, headers=headers)
        print(rsp.json())
        self.record_list = rsp.json()['listValue']
        self.RaceNums = rsp.json()['RaceNums']
        self.RaceMNums = rsp.json()['RaceMNums']
        return rsp.json()

    # 检测今日是否有跑步数据
    def check_today(self):
        # self.get_info()
        # self.download()
        # record_list = self.download()['listValue']
        if not self.record_list:
            return False
        # print(record_list)
        # 获取当前时间
        now_time = str(datetime.datetime.now().year) + '年' + str(datetime.datetime.now().month) + '月' + str(
            datetime.datetime.now().day) + '日'
        if len(str(datetime.datetime.now().day)) == 1:
            now_time = str(datetime.datetime.now().year) + '年' + str(datetime.datetime.now().month) + '月' + "0" + str(
                datetime.datetime.now().day) + '日'
        # print(now_time)
        # print(record_list)
        if self.record_list[0]['ResultDate'] == now_time:
            return True
        else:
            return False

    # 获取所有信息
    def get_all_info(self):
        self.get_info()
        self.get_RunId()
        self.upload()
        self.download()


if __name__ == '__main__':
    # testA = Aipaoer('777c75b73d5e480981a43444c7c2f934')
    # testA = Aipaoer('9eefdb3109ef4e5da3dde640e2b5c21e')
    # testA.imei_check()
    # print(testA.RaceNums)
    # print(testA.RaceMNums)
    # print(testA.record_list)
    # testA.get_info()
    # testA.get_RunId()
    # if testA.upload():
    #     print('ok')
    # if testA.check_today():
    #    print("today...ok")
    txt_path = "C:\\Users\\21421\\Desktop\\YGTY\\ygty.txt"  # txt文本路径
    f = open(txt_path)
    data_lists = f.readlines()  # 读出的是str类型

    dataset = []
    # 对每一行作循环
    for data in data_lists:
        data1 = data.strip('\n')  # 去掉开头和结尾的换行符
        data2 = data1.split('\t')  # 把tab作为间隔符
        dataset.append(data2)  # 把这一行的结果作为元素加入列表dataset

    for i in range(len(dataset)):
        str1 = ''.join(dataset[i])
        print(str1)
        testA = Aipaoer(str1)
        testA.imei_check()
        print(testA.RaceNums)
        print(testA.RaceMNums)
        print(testA.record_list)