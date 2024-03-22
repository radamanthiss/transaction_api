import json
import os
import pytest
from moto import mock_aws
from unittest.mock import patch, MagicMock
from src.lambda_function import lambda_handler
import boto3

# Setup mock S3
@pytest.fixture
def aws_credentials():
  """Mocked AWS Credentials for moto."""
  os.environ["AWS_ACCESS_KEY_ID"] = "testing"
  os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
  os.environ["AWS_REGION"] = "us-east-1"

@pytest.fixture
def s3_setup(aws_credentials):
  with mock_aws():
    s3 = boto3.resource('s3', region_name="us-east-1")
    s3.create_bucket(Bucket='stori-challenge-transaction-bucket')
    obj = s3.Object('stori-challenge-transaction-bucket', 'uploads/stori_challenge_123.csv')
    obj.put(Body=json.dumps({'test': 'data'}))
    yield

# Setup mock DynamoDB
@pytest.fixture
def dynamodb_setup(aws_credentials):
  with mock_aws():
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.create_table(
        TableName='transactions',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )
    
    # Add optional: insert mock data into the table here

    table.meta.client.get_waiter('table_exists').wait(TableName='transactions')
    yield

@pytest.fixture
def email_manager_mock():
  with patch('src.lambda_function.EmailManager') as mock:
    yield mock

@pytest.fixture
def dynamodb_manager_mock():
  with patch('src.lambda_function.DynamoDBManager') as mock:
    yield mock
    
def test_lambda_handler(s3_setup, dynamodb_setup, email_manager_mock, dynamodb_manager_mock):
  mock_event = {
      'Records': [{
          's3': {
              'bucket': {'name': 'stori-challenge-transaction-bucket'},
              'object': {'key': 'uploads/stori_challenge_123.csv'}
          }
      }],
      'running_type': 'local'
  }
  
  # Mocking get_email to return a fixed value
  with patch('src.lambda_function.get_email', return_value='test@example.com'):
      response = lambda_handler(mock_event, None)
  
  assert response['statusCode'] == 200
  assert 'Successfully processed transactions' in response['body']


# @pytest.fixture
# def dynamodb_table(aws_credentials):
#   with mock_aws():
#     dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
#     dynamodb.create_table(
#         TableName='accounts',
#         KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
#         AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
#         ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
#     )
#     dynamodb.meta.client.get_waiter('table_exists').wait(TableName='accounts')

# @pytest.fixture
# def s3_setup(aws_credentials):
#   with mock_aws():
#     s3 = boto3.client('s3', region_name='us-east-1')
#     s3.create_bucket(Bucket='stori-challenge-transaction-bucket')
#     s3.put_object(Bucket='stori-challenge-transaction-bucket', Key='uploads/stori_challenge_123.csv', Body="Id;AccountId;Date;Transaction\n1;1;jul-23;10.1\n2;1;jul-23;-8.2")
#     yield

# @pytest.fixture
# def mock_email_manager(monkeypatch):
#   mock_send_email = MagicMock(return_value={'MessageId': 'mock_message_id'})
#   monkeypatch.setattr("src.email_manager.EmailManager", mock_send_email)
#   return mock_send_email

# @pytest.fixture
# def mock_email_template(monkeypatch):
#   template_content = "<html><body><h1>Monthly Summary</h1><p>Balance: $100.0</p></body></html>"
#   monkeypatch.setattr("builtins.open", mock_open(read_data=template_content))
  
# def test_lambda_handler_success(dynamodb_table, s3_setup, mock_email_manager, mock_email_template):
#   mock_email_manager.return_value = {'MessageId': 'mock_message_id'}

#   """Test the lambda handler for a successful process."""
#   event = {
#     "Records": [
#       {
#         "s3": {
#           "bucket": {
#             "name": "stori-challenge-transaction-bucket"
#           },
#           "object": {
#             "key": "uploads/stori_challenge_123.csv"
#           }
#         }
#       }
#     ]
#   }
#   context = {}
#   s3 = boto3.client('s3', region_name='us-east-1')
#   csv_content = 'Id;AccountId;Date;Transaction\n1;1;jul-23;+10.1\n2;1;jul-23;-8.2'
#   s3.put_object(Bucket='stori-challenge-transaction-bucket', Key='uploads/stori_challenge_123.csv', Body=csv_content)

#   response = lambda_handler(event, context)
#   assert response['statusCode'] == 200
#   assert 'Successfully processed transactions and sent summary email.' in response['body']
  
#   mock_email_manager.assert_called_once_with(
#     recipient="ksanchez9306@gmail.com",  # Use ANY from unittest.mock or specific expected value
#     subject="Summary test",  # Same as above
#     html_content=""  # Same as above or test for specific content
#   )
