import re
import json
import logging
import datetime
import platform
import smtplib
import traceback
from pathlib import Path
from typing import List, Optional
from email.message import Message
from email.mime.text import MIMEText
from multiprocessing.pool import ThreadPool as Pool


class EmailSender:
    EMAIL_HOST = "smtp.qq.com"
    EMAIL_PORT = 465

    def __init__(self, user: str, password: str, receivers: List[str], output_path: str):
        self.email_user = user
        self.email_pass = password
        self.receivers = receivers

        self.output_path = Path(output_path)
        self.output_name = output_path.name.split('_')[-1]

    def make_finish_message(self, seq_num, img_num, phase):
        body = (
            f'From {platform.node()}\n'
            f'Output path: "{self.output_path}"\n\n'
            f'message:\n'
            f"    Pipline finished!\n"
            f'    seq_num: {seq_num}\n'
            f'    img_num: {img_num}\n'
            "\n\n"
            f"{datetime.datetime.now().isoformat()}"
        )
        message = MIMEText(body, 'plain', 'utf8')
        message['From'] = f'XRFeitoriaGear<{self.email_user}>'
        message['To'] = ','.join(self.receivers)
        message['Subject'] = f"[{self.output_name}] {phase} Finished: {seq_num}/{seq_num} @{platform.node()}"
        return message

    def make_message(self, i_current, n_total, phase, remaining_time: str=None):
        body = (
            f"From {platform.node()}\n"
            f'Output path: "{self.output_path}"\n\n'
            "message:\n"
            f"    Current step: {phase}\n"
            f"    Finished {i_current} sequences of totally {n_total}\n"
            f"    Percentage: {i_current/n_total:.2%}\n"
            f"    {phase} remaining time: {remaining_time}\n"
            "\n\n"
            f"{datetime.datetime.now().isoformat()}"
        )
        message = MIMEText(body, 'plain', 'utf8')
        message['From'] = f'XRFeitoriaGear<{self.email_user}>'
        message['To'] = ','.join(self.receivers)
        message['Subject'] = f"[{self.output_name}] {phase}: {i_current}/{n_total} @{platform.node()}"
        return message

    @staticmethod
    def _send_email(
        msg: Message,
        mail_host: str,
        mail_port: int,
        mail_user: str,
        mail_pass: str
    ):
        try:
            with smtplib.SMTP_SSL(mail_host, mail_port) as smtp:
                smtp.connect(mail_host, mail_port)
                smtp.login(mail_user, mail_pass)
                smtp.send_message(msg)
        except Exception:
            error_msg = f"EMAIL SENDING FAILED!\n{traceback.format_exc()}"
            logging.error(error_msg)
            return False, error_msg
        else:
            return True, "Mail sended!"

    def send(self, i_current, n_total, phase, remaining_time: str=None):
        msg = self.make_message(i_current, n_total, phase, remaining_time)
        self._send_email(
            msg,
            mail_host=self.EMAIL_HOST,
            mail_port=self.EMAIL_PORT,
            mail_user=self.email_user,
            mail_pass=self.email_pass,
        )

    def send_finish(self, seq_num, img_num, phase):
        msg = self.make_finish_message(seq_num, img_num, phase)
        self._send_email(
            msg,
            mail_host=self.EMAIL_HOST,
            mail_port=self.EMAIL_PORT,
            mail_user=self.email_user,
            mail_pass=self.email_pass,
        )

def get_email_sender() -> Optional['EmailSender']:
    email_json = Path(__file__).with_name("email.json")
    if email_json.exists():
        with open(email_json, "r") as f:
            settings = json.load(f)
        sender = EmailSender(
            settings['username'],
            settings['password'],
            settings['receivers'],
        )
        return sender
    else:
        logging.error("Email sender does not get setup.")
