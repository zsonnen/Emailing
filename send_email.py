import os
import mimetypes
import random
import smtplib
from email import encoders, mime
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple


CLIENT_NAME = "Me"

EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

""" If you wish to try this out: uncomment out the two lines below"""
# EMAIL_ADDRESS = input("Enter your Email Address: ")
# EMAIL_PASSWORD = input("Enter your password")

FILENAME = os.path.basename(__file__)

class MyEmail:

    def __init__(self, sender, recipient, subject, msg_html, msg_text, attachment_files=[]):
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.msg_html = msg_html
        self.msg_text = msg_text
        self.attachments = attachment_files
        self.email_msg = self.create_message()
    
    def create_message(self) -> MIMEMultipart:
        message = MIMEMultipart('mixed')
        message['from'] = self.sender
        message['to'] = self.recipient
        message['subject'] = self.subject

        msg_alternative = MIMEMultipart('alternative')
        msg_related = MIMEMultipart('related')

        msg_related.attach(MIMEText(self.msg_html, 'html'))
        msg_alternative.attach(MIMEText(self.msg_text, 'plain'))
        msg_alternative.attach(msg_related)

        message.attach(msg_alternative)
        message = self.attach_files(message)
        
        return message
    
    def attach_files(self, message: MIMEMultipart) -> MIMEMultipart:
        if self.attachments:
            for file in self.attachments:                
                content_type, encoding = mimetypes.guess_type(file)
                if file[-3:] == '.py':
                    content_type = 'application/octet-stream'
                if content_type is None or encoding is not None:
                    content_type = 'application/octet-stream'
                main_type, sub_type = content_type.split('/', 1)

                with open(file, 'rb') as f:
                    file_data = f.read()
                    file_name = f.name
                    if main_type == 'text':
                        msg = MIMEText(file_data, _subtype=sub_type)
                    elif main_type == 'image':
                        msg = MIMEImage(file_data, _subtype=sub_type)
                    elif main_type == 'pdf':
                        msg = MIMEApplication(file_data, _subtype=sub_type)
                    elif main_type == 'audio':
                        msg = MIMEAudio(file_data, _subtype=sub_type)
                    else:
                        msg = MIMEBase(main_type, sub_type)
                        msg.set_payload(file_data)  

                encoders.encode_base64(msg)
                msg.add_header('Content-Disposition', 'attachment', filename=file_name)
                message.attach(msg)

        return message
    
    def send_email(self, EMAIL_ADDRESS: str, EMAIL_PASSWORD: str, message: MIMEMultipart) -> None:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) 
            smtp.send_message(message) 


def get_info(name: str) -> str:
    with open('info.txt', 'r') as f:
        data = dict(line.rstrip().split(': ') for line in f) 
    client_data = data[name]

    return client_data

def get_youtube_vid() -> str:
    with open("youtube.txt", 'r') as f:
        data = [line.rstrip() for line in f]
        random_num = random.randint(0, len(data)-1)
        video = data[random_num]
    return video 

def personalize_message() -> tuple:
    
    msg = """
    Thank you for accepting to be a volunteer source of my message tests :D! 
    Of course, sending you a reminder to go workout!
    - always try to stay active in anyway possible!
    In anycase this was just a trial run.
    """.split('\n')

    url = get_youtube_vid()
    url_text = "YOUR YOUTUBE VIDEO OF THE DAY! (Click To Watch)"

    reply = "If there are specific categories of video's you would enjoy, please feel free to reply with that info."

    note = "Note: the actual python script I wrote to send this email is attached! (if you would want to look)"
    
    signature = "- this message written to you using python\n- ZS".split('\n')

    p_s = "If you have any feedback, as it pertains to color choice, or overall design etc. feel free to reply!\n\
         I realize my color blindness might be a slight problem in this area, but I welcome any input!".split('\n')

    return (msg, url, url_text, reply, note, signature, p_s)


def main():
    _recipient = get_info(CLIENT_NAME)

    # Set RECIPIENT to EMAIL_ADDRESS to send to yourself
    RECIPIENT = EMAIL_ADDRESS
    # RECIPIENT = _recipient

    MSG, URL, URL_TEXT, REPLY, NOTE, SIGNATURE, P_S = personalize_message()

    subject = "Message from [ZS]!"
    msg_text = "Regular text email: fallback if the html doesn't load. Hopefully you don't see this!"

    h_text = "Harnassing the power of python (and HTML)"
    
    # Emails don't support css or the html <style> tag (at least with regards to gmail)
    # My workaround was injecting these strings as inline styles
    body_style = "background-color:#e7e7e7;"
    h2_style = "color: #003366"
    h4_style = "color: #3F3F3F"

    p_style1 = "color: #003366"
    p_style2 = "color: #3F3F3F; font-style: italic;"

    msg_html = f"""\
    <!DOCTYPE html>
    <html>
        <body style="{body_style}">
            <h2 style="{h2_style}"><strong>Hey {CLIENT_NAME}!</strong></h2>
            <h4 style="{h4_style}"><strong><i>{h_text}</i></strong></h4>            
            <p style="{p_style1}">{MSG[1]}</p>    
            <p style="{p_style1}">
                Sending you:
                <br/>
                <a href="{URL}" target="_parent"><button>{URL_TEXT}</button></a>
            </p>
            <p style="{p_style1}">{REPLY}</p>
            <p style="{p_style1}">
                {MSG[2]}
                <br/>
                {MSG[3]}
            </p>
            <p style="{p_style1}">{MSG[4]}</p>            
            <p style="{p_style1}">{NOTE}</p>
            <p style="{p_style2}">
                {SIGNATURE[0]}
                <br/>
                {SIGNATURE[1]}
            </p>
            <p style="{p_style2}">
                <strong>P.S!</strong>
                <br/>{P_S[0]}
                <br/>{P_S[1]}
            </p> 
        </body>
    </html>  
    """
    
    #A couple attachments, for example purposes
    files = ['snowboard.jpg', FILENAME] 

    my_email = MyEmail(EMAIL_ADDRESS, RECIPIENT, subject, msg_html, msg_text, files)

    message = my_email.create_message()
    my_email.send_email(EMAIL_ADDRESS, EMAIL_PASSWORD, message)
    
    print("message sent!")


if __name__ == '__main__':
    main()


