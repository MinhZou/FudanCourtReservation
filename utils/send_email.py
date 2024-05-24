import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header

def send_mail(now_time, scheduled_time, court, username, user):
    sender = '770445973@qq.com'
    # user = '770445973@qq.com'
    flag = True
    try:
        msg = MIMEText('已成功预定{}-{}的球场！！！'.format(court, scheduled_time), "plain", 'utf-8')
        msg["Subject"] = Header('{}{}羽毛球场已于{}成功预定，请查看！！！'.format(scheduled_time, court, now_time), 'utf-8') 
        msg["From"] = formataddr(['Minhzou', sender]) 
        msg["To"] = formataddr([username, user]) 

        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.login(sender, 'xxx')
        s.sendmail(sender, [user, ], msg.as_string()) 
        s.quit() 
        # print("邮件发送成功！")
    except Exception as msg:
        flag = False
        # print(msg)
        # print("邮件发送失败")
    return flag