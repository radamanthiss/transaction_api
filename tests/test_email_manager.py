import pytest
from botocore.stub import Stubber
import boto3
from src.email_manager import EmailManager
import os
from unittest.mock import patch, MagicMock, ANY


@pytest.fixture
def ses_client_stub():
  """Fixture for creating a stubbed SES client."""
  client = boto3.client('ses', region_name='us-east-1')
  stubber = Stubber(client)
  stubber.activate()
  yield client, stubber
  stubber.deactivate()
  
@pytest.fixture
def email_manager_ses(ses_client_stub):
  """Fixture for creating an EmailManager instance configured for SES, using a stubbed SES client."""
  client, _ = ses_client_stub
  manager = EmailManager(sender='ulkevinb@gmail.com', aws_region='us-east-1', running_type='prod')
  manager.client = client  # Directly replace the SES client with the stubbed client
  return manager


@pytest.fixture
def email_manager_smtp(monkeypatch):
  """Fixture for creating an EmailManager instance configured for SMTP with environment variables set."""
  monkeypatch.setenv('SMTP_SERVER', 'localhost')
  monkeypatch.setenv('SMTP_PORT', '1025')
  monkeypatch.setenv('SMTP_USER', 'user')
  monkeypatch.setenv('SMTP_PASSWORD', 'password')
  return EmailManager(sender='ulkevinb@gmail.com', running_type='local')

@pytest.fixture
def recipient():
  return 'ksanchez9306@gmail.com'

@pytest.fixture
def subject():
  return 'Subject'

@pytest.fixture
def html_body():
  return '<h1>Test html</h1>'

def test_send_email_ses(email_manager_ses, ses_client_stub, recipient, subject, html_body):
  _ , stubber = ses_client_stub
  expected_response = {'MessageId': '1234'}
  
  # Add a response to the SES client stub
  stubber.add_response('send_email', expected_response, {
    'Source': email_manager_ses.sender,
    'Destination': {'ToAddresses': [recipient]},
    'Message': {
      'Subject': {'Data': subject},
      'Body': {'Html': {'Data': html_body}}
    }
  })
  
    
  # Ensure the stubber is used for the duration of this test
  with stubber:
    # Call the method under test
    response = email_manager_ses.send_email(recipient, subject, html_body)
    
    # Assertions
    assert response == expected_response
    stubber.assert_no_pending_responses()  # Verify all expected responses were used



def test_send_email_smtp(email_manager_smtp, recipient, subject, html_body):
  with patch('smtplib.SMTP') as mock_smtp:
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    
    # Call the method under test
    response = email_manager_smtp.send_email(recipient, subject, html_body)
    
    # Assertions
    assert response == {'MessageId': 'Email sent with smtp'}
    mock_smtp.assert_called_once_with('localhost', 1025)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with('user', 'password')
    mock_server.sendmail.assert_called_once_with(email_manager_smtp.sender, recipient, ANY)
    mock_server.quit.assert_called_once()

