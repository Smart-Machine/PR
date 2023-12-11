from smtplib import SMTP_SSL as SMTP


class MailService:

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.connection = None

    def auth(self, username, password):
        try:
            self.connection = SMTP(self.host)
            response = self.connection.login(username, password)
            if len(response) > 1 and b"Accepted" in response[1]:
                return True
        except:
            return False

    def send_mail(self, sender, receiver, subject, content):
        try:
            message = f"From: {sender}\nTo: {receiver}\nSubject: {subject}\n\n{content}"
            self.connection.sendmail(sender, receiver, message)
            return True
        except:
            return False
