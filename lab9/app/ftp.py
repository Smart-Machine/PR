import os
from ftplib import FTP


class FTPService:

    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

        self.link = None

    def upload(self, file_path):
        try:
            ftp_server = FTP(self.host)
            ftp_server.login(self.username, self.password)

            # with open(f"{file_name}", "w") as file_tmp:
            #     file_tmp.write(file_content)

            with open(file_path, "rb") as file_pointer:
                ftp_server.storbinary(f"STOR {os.path.basename(file_path)}", file_pointer)

            self.link = f"ftp://{self.username}:{
                self.password}@{self.host}/{os.path.basename(file_path)}"

            os.remove(file_path)
            ftp_server.quit()
            return True
        except:
            return False
