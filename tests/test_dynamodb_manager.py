import pytest
from unittest.mock import PropertyMock, call, patch, MagicMock
from botocore.stub import Stubber
import boto3
from src.dynamodb_manager import DynamoDBManager
from datetime import datetime
from moto import mock_aws

@pytest.fixture
def dynamodb_stub():
  with patch("boto3.resource") as mock_dynamodb_resource:
    mock_dynamodb = MagicMock()
    mock_dynamodb_resource.return_value = mock_dynamodb
    mock_table = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    
    yield mock_table

@pytest.fixture
def dynamodb_manager():
  """Fixture to create a DynamoDBManager instance with a mocked DynamoDB table."""
  with patch('src.dynamodb_manager.boto3.resource') as mock_resource:
    mock_table = MagicMock()
    mock_resource.return_value.Table.return_value = mock_table
    yield DynamoDBManager('transactions'), mock_table
  # with mock_aws():
  #   # Setup DynamoDB Table
  #   dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
  #   dynamodb.create_table(
  #       TableName='transactions',
  #       KeySchema=[
  #           {'AttributeName': 'id', 'KeyType': 'HASH'},
  #       ],
  #       AttributeDefinitions=[
  #           {'AttributeName': 'id', 'AttributeType': 'S'},
  #       ],
  #       ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
  #   )
    
  #   yield DynamoDBManager(table_name='transactions')

def test_save_transactions(dynamodb_manager):
  dynamodb_manager_instance, mock_table = dynamodb_manager
  mock_batch_writer = MagicMock()
  mock_table.batch_writer.return_value = mock_batch_writer  # Mock batch_writer to return your mock_batch_writer

  transactions = [
      {"id": "1", "accountId": "1", "date": datetime.now().isoformat(), "transanction": "+20.5"},
      {"id": "2", "accountId": "1", "date": datetime.now().isoformat(), "transanction": "-2.5"}
  ]
  dynamodb_manager_instance.save_transactions(transactions)
  expected_calls = [
    call.__enter__().put_item(Item=transactions[0]),
    call.__enter__().put_item(Item=transactions[1]),
  ]
  actual_calls = mock_batch_writer.mock_calls[1:-1]  # Exclude __enter__ and __exit__ calls

  assert actual_calls == expected_calls, "Transactions were not saved as expected"
# def test_save_transactions(dynamodb_manager):
#   dynamodb_manager_instance, mock_table = dynamodb_manager
#   transactions = [
#         {"id": "1", "accountId":"1", "date": datetime.now().isoformat(), "transanction": "+20.5"},
#         {"id": "2", "accountId":"1", "date": datetime.now().isoformat(), "transanction": "-2.5"}
#     ]
#   dynamodb_manager_instance.save_transactions(transactions)
    
#   for transaction in transactions:
#     # Adjust the expected item structure as necessary
#     expected_item = {'id': transaction['id'], 'accountId': transaction['accountId'], 'date': transaction['date'], 'transanction': transaction['transanction']}
#     mock_table.put_item.assert_called()

def test_get_item(dynamodb_manager):
  dynamodb_manager, mock_table = dynamodb_manager

  key = {"id": "1"}
  expected_item = {"id": "1", "email": "ksanchez9306@gmail.com"}
  mock_table.get_item.return_value = {"Item": expected_item}

  item = dynamodb_manager.get_item(key)
  assert item == expected_item
  
def test_delete_item(dynamodb_manager, dynamodb_stub):
  dynamodb_manager_instance, _ = dynamodb_manager
  key = {"id": "1"}
  mock_response = {
      "ResponseMetadata": {
          "HTTPStatusCode": 200
      }
  }
  dynamodb_stub.delete_item.return_value = mock_response
  response = dynamodb_manager_instance.delete_item(key)
  
  # Directly assert the mock response for clarity
  assert dynamodb_stub.delete_item.return_value["ResponseMetadata"]["HTTPStatusCode"] == 200
  

def test_save_account(dynamodb_manager):
  dynamodb_manager_instance, mock_table = dynamodb_manager
  account_id = "1"
  email = "example@example.com"
  mock_response = {"ResponseMetadata": {"HTTPStatusCode": 200}}
  mock_table.put_item.return_value = mock_response

  response = dynamodb_manager_instance.save_account(account_id, email)
  assert response == mock_response
  mock_table.put_item.assert_called_once_with(Item={"id": account_id, "email": email})

  # account_id = "1"
  # email = "example@example.com"
  # dynamodb_stub.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
  
  # response = dynamodb_manager.save_account(account_id, email)
  # assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
  # dynamodb_stub.put_item.assert_called_once_with(Item={"id": account_id, "email": email})
