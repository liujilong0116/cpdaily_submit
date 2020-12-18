import requests
import json
import time
import pyDes
import base64
import uuid
import sys
import yaml
from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText

from urllib3.exceptions import InsecureRequestWarning
# debug模式
debug = False
if debug:
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 获取当前utc时间，并格式化为北京时间
def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")

# 输出调试信息，并及时刷新缓冲区
def log(content):
    print(getTimeStr() + ' ' + str(content))
    sys.stdout.flush()

# 加载配置文件
def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)

    return dict(config)



# 全局配置
config = getYmlConfig(yaml_file='config.yml')

#可使用邮箱自动
mail_host = 'smtp.163.com'
#163用户名
mail_user = 'xxx'
#密码(部分邮箱为授权码)
mail_pass = 'xxx'
#邮件发送方邮箱地址
sender = 'xxx'

def sendMessage(receiver, msg):
    if receiver != '':
        # 邮件内容设置
        message = MIMEText(msg, 'plain', 'utf-8')
        # 邮件主题
        message['Subject'] = '%s.%s今日校园打卡结果'%(datetime.now().month, datetime.now().day)
        # 发送方信息
        message['From'] = sender
        # 接受方信息
        message['To'] = receiver
        receivers = [receiver]
        try:
            smtpObj = smtplib.SMTP()

            # 连接到服务器
            smtpObj.connect(mail_host, 25)
            # 登录到服务器
            smtpObj.login(mail_user, mail_pass)
            # 发送
            smtpObj.sendmail(
                sender, receivers, message.as_string())
            time.sleep(5)
            # 退出
            smtpObj.quit()
            log('发送邮件通知成功。。。')
        except smtplib.SMTPException as e:
            log('发送邮件通知失败。。。')

class Auto_Submit:
    def __init__(self, host="sise"):
        self.key = "ST83=@XV"  # dynamic when app update
        self.t = str(int(round(time.time() * 1000)))
        self.session = requests.session()
        self.host = host + ".campusphere.net"
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Pragma": "no-cache",
            "Accept": "application/json, text/plain, */*",
            # "User-Agent": "okhttp/3.12.4"
        })
        url = "https://{host}/iap/login?service=https://{host}/portal/login".format(host=self.host)
        ret = self.session.get(url).url
        self.client = ret[ret.find("=") + 1:]
        self.session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        url = "https://{host}/iap/security/lt".format(host=self.host)
        ret = json.loads(self.session.post(url, data="lt={client}".format(client=self.client)).text)
        self.client = ret["result"]["_lt"]
        self.encryptSalt = ret["result"]["_encryptSalt"]

    def encrypt(self, text):
        k = pyDes.des(self.key, pyDes.CBC, b"\x01\x02\x03\x04\x05\x06\x07\x08", pad=None, padmode=pyDes.PAD_PKCS5)
        ret = k.encrypt(text)
        return base64.b64encode(ret).decode()

    def decrypt(self, text):
        k = pyDes.des(self.key, pyDes.CBC, b"\x01\x02\x03\x04\x05\x06\x07\x08", pad=None, padmode=pyDes.PAD_PKCS5)
        ret = k.decrypt(base64.b64decode(text))
        return ret.decode()

    def checkNeedCaptcha(self, username):
        url = "https://{host}/iap/checkNeedCaptcha?username={username}&_=".format(host=self.host, username=username)
        ret = self.session.get(url)
        ret = json.loads(ret.text)
        return ret["needCaptcha"]

    def generateCaptcha(self):
        url = "https://{host}/iap/generateCaptcha?ltId={client}&codeType=2&".format(host=self.host, client=self.client)
        ret = self.session.get(url)
        return ret.content

    def getBasicInfo(self):
        url = "https://{host}/iap/tenant/basicInfo".format(host=self.host)
        ret = self.session.post(url, data="{}").text
        return json.loads(ret)

    def login(self, username, password, captcha=""):
        url = "https://{host}/iap/doLogin".format(host=self.host)
        self.username = username
        body = {
            "username": username,
            "password": password,
            "lt": self.client,
            "captcha": captcha,
            "rememberMe": "true",
            "dllt": "",
            "mobile": ""
        }
        self.session.headers["Content-Type"] = "application/x-www-form-urlencoded"
        ret = json.loads(self.session.post(url, data=body).text)
        if ret["resultCode"] == "REDIRECT":
            self.session.get(ret["url"])
            return True
        else:
            return False

    def getCollectorList(self):
        body = {
            "pageSize": 10,
            "pageNumber": 1
        }
        self.session.headers["Content-Type"] = "application/json"
        url = "https://{host}/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList".format(
            host=self.host)
        ret = self.session.post(url, data=json.dumps(body))
        ret = json.loads(ret.text)
        return ret["datas"]["rows"]

    def getNoticeList(self):
        body = {
            "pageSize": 10,
            "pageNumber": 1
        }
        self.session.headers["Content-Type"] = "application/json"
        url = "https://{host}/wec-counselor-stu-apps/stu/notice/queryProcessingNoticeList".format(host=self.host)
        ret = self.session.post(url, data=json.dumps(body))
        ret = json.loads(ret.text)
        return ret["datas"]["rows"]

    def confirmNotice(self, wid):
        body = {
            "wid": wid
        }
        self.session.headers["Content-Type"] = "application/json"
        url = "https://{host}/wec-counselor-stu-apps/stu/notice/confirmNotice".format(host=self.host)
        ret = self.session.post(url, data=json.dumps(body))
        ret = json.loads(ret.text)
        if ret["message"] == "SUCCESS":
            return True
        else:
            log(ret["message"])
            return False

    def getCollectorDetail(self, collectorWid):
        url = "https://{host}/wec-counselor-collector-apps/stu/collector/detailCollector".format(host=self.host)
        body = {
            "collectorWid": collectorWid
        }
        self.session.headers["Content-Type"] = "application/json"
        ret = self.session.post(url, data=json.dumps(body))
        ret = json.loads(ret.text)["datas"]
        url = ret["form"]["formContent"]
        return ret

    def getCollectorFormFiled(self, formWid, collectorWid):
        url = "https://{host}/wec-counselor-collector-apps/stu/collector/getFormFields".format(host=self.host)
        body = {
            "pageSize": 50,
            "pageNumber": 1,
            "formWid": formWid,
            "collectorWid": collectorWid
        }
        self.session.headers["Content-Type"] = "application/json"
        ret = self.session.post(url, data=json.dumps(body))
        ret = json.loads(ret.text)["datas"]["rows"]
        return ret

    def submitCollectorForm(self, formWid, collectWid, schoolTaskWid, rows, address, email):
        url = "https://{host}/wec-counselor-collector-apps/stu/collector/submitForm".format(host=self.host)
        body = {
            "formWid": formWid,
            "collectWid": collectWid,
            "schoolTaskWid": schoolTaskWid,
            "form": rows,
            "address": address
        }
        self.session.headers["Content-Type"] = "application/json"
        # self.session.headers["extension"] = "1" extension
        extension = {"deviceId": str(uuid.uuid4()), "systemName": "未来操作系统", "userId": self.username,
                     "appVersion": "8.1.13", "model": "红星一号量子计算机", "lon": 0.0, "systemVersion": "初号机", "lat": 0.0}
        self.session.headers.update({"Cpdaily-Extension": self.encrypt(json.dumps(extension))})
        ret = self.session.post(url, data=json.dumps(body))
        log(ret.text)
        ret = json.loads(ret.text)
        if ret["message"] == "SUCCESS":
            sendMessage(email, '自动提交成功！')
            return True
        else:
            log(ret["message"])
            return False

    # 自动填写表单内容
    def autoFill(self, form):
        sort = 1
        for formItem in form[:]:
            # 只处理必填项
            if formItem['isRequired'] == 1:
                default = config['cpdaily']['defaults'][sort - 1]['default']
                if formItem['title'] != default['title']:
                    log('第%d个默认配置不正确，请检查' % sort)
                    exit(-1)
                # 文本直接赋值
                if formItem['fieldType'] == 1:
                    formItem['value'] = default['value']
                    if formItem['title'] == '今日晚间返回宿舍（家）时间':
                        formItem['value'] = '%s/%s/%s/21/30' % (
                        datetime.now().year, datetime.now().month, datetime.now().day)
                # 单选框需要删掉多余的选项
                if formItem['fieldType'] == 2:
                    # 填充默认值
                    formItem['value'] = default['value']
                    fieldItems = formItem['fieldItems']
                    for i in range(0, len(fieldItems))[::-1]:
                        if fieldItems[i]['content'] != default['value']:
                            del fieldItems[i]
                # 多选需要分割默认选项值，并且删掉无用的其他选项
                if formItem['fieldType'] == 3:
                    fieldItems = formItem['fieldItems']
                    defaultValues = default['value'].split(',')
                    for i in range(0, len(fieldItems))[::-1]:
                        flag = True
                        for j in range(0, len(defaultValues))[::-1]:
                            if fieldItems[i]['content'] == defaultValues[j]:
                                # 填充默认值
                                formItem['value'] += defaultValues[j] + ' '
                                flag = False
                        if flag:
                            del fieldItems[i]
                sort += 1
            else:
                form.remove(formItem)

    # 提交表单
    def autoComplete(self, address, email):
        collectList = self.getCollectorList()
        log(collectList)
        if str(collectList) == 'None':
            log('获取最新待填写问卷失败，可能是辅导员还没有发布。。。')
            sendMessage(email, '尚未发布打卡')
            exit(-1)

        for item in collectList:
            detail = self.getCollectorDetail(item["wid"])

            form = self.getCollectorFormFiled(
                detail["collector"]["formWid"], detail["collector"]["wid"])
            self.autoFill(form)
            self.submitCollectorForm(detail["collector"]["formWid"], detail["collector"]
            ["wid"], detail["collector"]["schoolTaskWid"], form, address, email)


def main_handler(event, context):
    for user in config['users']:
        user = user['user']


        school = user['school']
        username = user['username']
        password = user['password']
        address = user['address']
        email= user['email']
        log("当前用户学号为："+ username)
        app = Auto_Submit(school)
        flag = 0
        while True:
            ret = app.login(username, password)
            time.sleep(1)
            if ret:
                log("登录成功")
                break
            else:
                flag = flag + 1
                log("登录失败，正在尝试第:" + str(flag) + "次")
            if flag >= 10:
                log("登录失败，退出程序")
                sys.exit()
        app.autoComplete(address, email)


if __name__ == "__main__":
    main_handler({}, {})