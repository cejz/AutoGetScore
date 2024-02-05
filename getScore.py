import requests
import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
import yaml

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

def get_score():
    s = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',  # 使用第三方库生成的随机UA
        'Referer': 'https://portal.pku.edu.cn/', 
    }
    login_url = 'https://iaaa.pku.edu.cn/iaaa/oauthlogin.do'
    form_data = {
        'appid': 'portal2017',
        'userName': str(config['user']['userName']),
        'password': str(config['user']['password']),
        'redirUrl': 'https://portal.pku.edu.cn/portal2017/ssoLogin.do'
    }
    res = s.post(login_url, headers=headers, data=form_data)
    try:
        token = res.json()["token"]
    except:
        print(res.text)
    res = s.get(f"https://portal.pku.edu.cn/portal2017/ssoLogin.do?_rand={random.random()}&token={token}")
    url = 'https://portal.pku.edu.cn/portal2017/bizcenter/score/retrScores.do'
    response = s.get(url, headers=headers) 
    return response.json() 

def send_email(email: str, score: str):
    mail_host = config["mail_server"]["mail_host"]
    mail_user = config["mail_server"]["mail_user"] 
    mail_pass = config["mail_server"]["mail_pass"]  
    
    receivers = [email] 

    message = MIMEText('有成绩更新：' + score, 'plain', 'utf-8')

    msg_from = "noreply "+"<"+ mail_user +">"
    message['From'] = Header(msg_from)
    message['To'] = Header(",".join(receivers), 'utf-8')

    subject = 'Score'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        smtpObj.verify_ssl = False
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(mail_user, receivers, message.as_string())
    except smtplib.SMTPException as e:
        print("Error: 无法发送邮件")
        print(e)

def main():
    kc = config['kc']
    while True:
        if not kc:
            break
        score_lists = get_score()["scoreLists"]
        res = ""
        for i in score_lists:
            if i["kcmc"] in kc:
                if i["cj"] != "":
                    res += f"{i['kcmc']}: {i['cj']} "
                    kc.remove(i["kcmc"])
        
        if res != "":
            send_email(config['user']['email'],res)
        
        time.sleep(config['interval'])
        
if __name__ == '__main__':
    main()
