import smtplib
from email.mime.text import MIMEText

def mailing(title, contents, mail):
    s = smtplib.SMTP('smtp.gmail.com',587)                          #구글 SMTP서버 사용
    s.starttls()
    s.login('tlsrudejr123@gmail.com','dllmwmsmcqjyklmf')
    msg = MIMEText(contents)                                        #mail 본문내용
    msg['Subject'] = title                                          #mail 제목
    s.sendmail("tlsrudejr123@gmail.com", mail, msg.as_string())
    s.quit()
