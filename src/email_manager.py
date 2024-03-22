from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
import boto3
import config

class EmailManager:
  def __init__(self, sender, aws_region='us-east-1', running_type='prod'):
    self.sender = sender
    self.running_type = running_type
    if self.running_type == 'prod':
      self.client = boto3.client('ses', region_name=aws_region)

  def send_email(self,recipient,subject,  html_body):
    if self.running_type == 'prod':
      response = self.client.send_email(
        Source=self.sender,
        Destination={
          'ToAddresses': [recipient]
        },
        Message={
          'Subject': {'Data': subject },
          'Body': {
            'Html': {'Data': html_body}
          }
        }
      )
      return response
      
    else:
      #for local testing
      smtp_server=os.getenv('SMTP_SERVER')
      smtp_port=int(os.getenv('SMTP_PORT'))
      smtp_user=os.getenv('SMTP_USER')
      smtp_password=os.getenv('SMTP_PASSWORD')
      #prepare message
      message = MIMEMultipart("alternative")
      message["Subject"] = subject
      message["From"] = self.sender
      message["To"] = recipient
      message.attach(MIMEText(html_body, "html"))
      # send email
      server = smtplib.SMTP(smtp_server, smtp_port)
      server.starttls()
      server.login(smtp_user, smtp_password)
      server.sendmail(self.sender, recipient, message.as_string())
      server.quit()
      return {'MessageId': 'Email sent with smtp'}
      
