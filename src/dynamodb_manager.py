from datetime import datetime
import boto3
import logging
import os
import config


class DynamoDBManager:
  def __init__(self, table_name):
    self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION'))
    self.table = self.dynamodb.Table(table_name)
    logging.info(f"Initializing DynamoDBManager with table name: {table_name}")


  def save_transactions(self, transactions):
    with self.table.batch_writer() as batch:
      for transaction in transactions:
        print(f"processing transaction: {transaction}")
        if isinstance(transaction['date'], datetime):
          transaction['date'] = transaction['date'].isoformat()
        batch.put_item(Item=transaction)

  def get_item(self, key):
    logging.info(f"Getting item from table {self.table.table_name} with key: {key}")

    try:
      response = self.table.get_item(Key=key)
      if 'Item' in response:
        return response['Item']
      else:
        logging.info(f"No item found with key: {key}")
        return None
    except Exception as e:
      logging.error(f"Error getting item: {e}")
      raise
    
  def delete_item(self, key):
    try:
      response = self.table.delete_item(Key=key)
      return response
    except Exception as e:
      logging.error(f"Error deleting item: {e}")
      raise
    
  def save_account(self, account_id, email):
    try:
      item = {'id': account_id, 'email': email}
      response = self.table.put_item(Item=item)
      return response
    except Exception as e:
      logging.error(f"Error saving account: {e}")
      raise