import logging
import traceback
import json
import os

from dynamodb_manager import DynamoDBManager
import config


# Configure basic logging
logging.basicConfig(level=logging.INFO)
DYNAMODB_ACCOUNTS_TABLE_NAME = os.getenv('DYNAMODB_ACCOUNTS_TABLE_NAME')

def lambda_handler(event, context):
  dynamo_db_manager = DynamoDBManager(DYNAMODB_ACCOUNTS_TABLE_NAME)
  logging.info(f"Accessing DynamoDB table: {DYNAMODB_ACCOUNTS_TABLE_NAME}")

  try:
    account_info = json.loads(event['body'])
  except (TypeError, ValueError) as e:
    traceback_str = ''.join(traceback.format_tb(e.__traceback__))
    error_message = f"Error try1: {str(e)}. Traceback: {traceback_str}"
    logging.error(error_message)
    return {'statusCode': 400, 'body': 'Invalid request body'}

  account_id = account_info['id']
  email = account_info['email']
  
  if not account_id or not email:
    return {'statusCode': 400, 'body': 'Missing account ID or email'}
  # Check if account already exists
  try:
    item = dynamo_db_manager.get_item({'id': account_id})
    if item:
      logging.info(f"Account already exists: {item}")
      return {'statusCode': 409, 'body': 'Account already exists'}
  except Exception as e:
    traceback_str = ''.join(traceback.format_tb(e.__traceback__))
    error_message = f"Error try2: {str(e)}. Traceback: {traceback_str}"
    logging.error(error_message)
    return {'statusCode': 500, 'body': 'Error accessing DynamoDB'}

  # Add new account
  try:
    dynamo_db_manager.save_account(account_id, email)
  except Exception as e:
    logging.error("Error saving new account to DynamoDB", exc_info=e)
    traceback_str = ''.join(traceback.format_tb(e.__traceback__))
    error_message = f"Error try3: {str(e)}. Traceback: {traceback_str}"
    logging.error(error_message)
    return {'statusCode': 500, 'body': 'Error saving account to DynamoDB'}

  return {'statusCode': 201, 'body': 'Account created successfully'}

