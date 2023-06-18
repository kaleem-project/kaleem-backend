import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import json
import os


class Message:

    def __init__(self, subject: str, receiver: str, body: str):
        self.message = MIMEMultipart("alternative")
        self.message["Subject"] = subject
        self.message["From"] = ""  # Kaleem Application Email Address
        self.message["To"] = receiver
        self.message.attach(MIMEText(body, "html"))

    def get_message(self):
        return self.message


class MailServer:

    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        self.__config_file = base_dir / "configs.json"
        with open(str(self.__config_file), "r") as json_file:
        # Read configuration from json file.
            conf = json.load(json_file)
        self.server = conf["mail_server_host"] 
        self.port = conf["mail_server_port"] 
        self.login_email = conf["mail_server_email"] 
        self.login_password = conf["mail_server_password"]

    def send(self, message):
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.server, self.port, context=context) as server:
            server.login(self.login_email, self.login_password)
            server.sendmail(self.login_email,
                            message["To"], message.as_string())


def load_reset_template() -> str:
    os.chdir(os.path.dirname(__file__))
    print(os.getcwd())
    with open("reset_password_template.html", "r") as template:
        content = template.read()
    return content

def load_confirmation_template() -> str:
    os.chdir(os.path.dirname(__file__))
    print(os.getcwd())
    with open("confirmation_template.html", "r") as template:
        content = template.read()
    return content


if __name__ == "__main__":
    email_server = MailServer()
