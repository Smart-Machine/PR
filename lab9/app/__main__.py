import getpass
from mail import MailService
from ftp import FTPService

FTP_HOST = "138.68.98.108"
FTP_USERNAME = "yourusername"
FTP_PASSWORD = "yourusername"

ftp_service = FTPService(FTP_HOST, FTP_USERNAME, FTP_PASSWORD)

MAIL_HOST = "smtp.gmail.com"
MAIL_PORT = 465

mail_service = MailService(MAIL_HOST, MAIL_PORT)


def mail_login_user():
    username = input("username: ")
    while not username:
        username = input("username: ")

    password = getpass.getpass("password: ")
    while not password:
        password = getpass.getpass("password: ")

    if not mail_service.auth(username, password):
        print("Wrong credentials")
        return False 

    print("Logged in the mail account")
    return True


def mail_form_user(): 
    sender = input("sender: ")
    while not sender:
        sender = input("sender: ")

    receiver = input("receiver: ")
    while not receiver:
        receiver = input("receiver: ")

    subject = input("subject: ")
    while not subject:
        subject = input("subject: ")

    content = input("content: ")
    while not content:
        content = input("content: ")

    file_path = input("file path: ") 
    while not file_path:
        file_path = input("file path: ")
    
    if not ftp_service.upload(file_path):
        print("Could not upload file")
        return False 
    print("File uploaded on the FTP server")

    content = f"{content}\n\n{ftp_service.link}"
    if not mail_service.send_mail(sender, receiver, subject, content):
        print("Could not send mail")
        return False 
    print("Email sent")
    return True

is_user_auth = mail_login_user()
while not is_user_auth:
    is_user_auth = mail_login_user()

while True:
    _ = mail_form_user()
    

