# import os
# import pytest
# from moto import mock_aws
# import boto3
# from src.lambda_account import lambda_handler
# from botocore.exceptions import ClientError

# @pytest.fixture(scope='function')
# def aws_credentials():
#     """Mocked AWS Credentials for moto."""
#     os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA6ODUZRWNKQOXKXCX'
#     os.environ['AWS_SECRET_ACCESS_KEY'] = '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'

# @pytest.fixture(scope='function')
# def dynamodb(aws_credentials):
#     with mock_aws():
#         yield boto3.resource('dynamodb', region_name='us-east-1')

# @pytest.fixture(scope='function')
# def create_table(dynamodb):
#     table = dynamodb.create_table(
#         TableName='accounts',
#         KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
#         AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
#         ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
#     )
#     return table

# def test_create_account_success(create_table):
#     """Test successful account creation."""
#     event = {'body': '{"id": "1", "email": "test@example.com"}'}
#     response = lambda_handler(event, None)
#     assert response['statusCode'] == 201
#     assert 'Account created successfully' in response['body']
    
#     # Verify that account is in the table
#     table = create_table
#     try:
#         response = table.get_item(Key={'id': '1'})
#         item = response['Item']
#         assert item['email'] == 'test@example.com'
#     except ClientError as e:
#         pytest.fail(f"DynamoDB get_item raised an exception: {e}")

# def test_create_account_existing_account(create_table):
#     """Test creating an account that already exists."""
#     table = create_table
#     table.put_item(Item={'id': '1', 'email': 'test@example.com'})
#     event = {'body': '{"id": "1", "email": "test@example.com"}'}
    
#     response = lambda_handler(event, None)
#     assert response['statusCode'] == 409
#     assert 'Account already exists' in response['body']

# def test_create_account_invalid_payload(create_table):
#     """Test account creation with an invalid payload."""
#     event = {'body': 'not a json'}
#     response = lambda_handler(event, None)
#     assert response['statusCode'] == 400
#     assert 'Invalid request body' in response['body']

# # More test cases as needed...
