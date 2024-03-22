from collections import defaultdict
import logging
from jinja2 import Environment, FileSystemLoader
from util import format_monthly_summaries, read_s3_file, parse_transactions, calculate_balance, calculate_overall_averages, calculate_transactions_by_month
from email_manager import EmailManager
from dynamodb_manager import DynamoDBManager
import os
import config

def get_email(account_id):
  dynamo_db_manager_account = DynamoDBManager(os.getenv('DYNAMODB_ACCOUNTS_TABLE_NAME'))
  print(f"table name: {os.getenv('DYNAMODB_ACCOUNTS_TABLE_NAME')}")
  try:
    account_id_str = str(account_id)
    response = dynamo_db_manager_account.get_item({'id': account_id_str})
    # If an item was found, return the email field
    if response:
      return response.get('email')
  except Exception as e:
    logging.error(f"Error retrieving email for account_id {account_id}: {e}")
  return None

def lambda_handler(event, context):
  running_type = event.get('running_type', 'prod')
  base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  print(f"base_dir: {base_dir}")
  env = Environment(loader=FileSystemLoader(os.path.join(base_dir, 'templates')))
  print(f"env: {env}")
  template = env.get_template('email_template.html')

  dynamo_db_manager = DynamoDBManager(os.getenv('DYNAMODB_TRANSACTIONS_TABLE_NAME'))
  print(f"table name: {os.getenv('DYNAMODB_TRANSACTIONS_TABLE_NAME')}")
  
  # Extract bucket name and file key from the Lambda event
  bucket_name = event['Records'][0]['s3']['bucket']['name']
  file_key = event['Records'][0]['s3']['object']['key']

  # Read the file content from S3
  file_content = read_s3_file(bucket_name, file_key)
  
  # process transacitons
  transactions = parse_transactions(file_content)
  transactions_by_account = defaultdict(list)
  for transaction in transactions:
    transactions_by_account[transaction['accountId']].append(transaction)
  
  # process transactions for each account and send an email
  for account_id, account_transactions in transactions_by_account.items():
    # Calculate summaries
    total_balance = calculate_balance(account_transactions)
    transactions_by_month = calculate_transactions_by_month(account_transactions)
    overall_averages = calculate_overall_averages(account_transactions)
    
    monthly_summaries_html = format_monthly_summaries(transactions_by_month)

    html_content = template.render({
      'total_balance': "{:.2f}".format(total_balance),
      'average_credit': "{:.2f}".format(overall_averages['average_credit']),
      'average_debit': "{:.2f}".format(overall_averages['average_debit']),
      'monthly_summaries': monthly_summaries_html
    })
    # Send email
    if running_type == 'prod':
      recipient_email = get_email(account_id)
    else :
      recipient_email = os.getenv('RECIPIENT_EMAIL')
    email_manager = EmailManager(os.getenv('SENDER_EMAIL'), os.getenv('AWS_REGION'), running_type=running_type)
    
    if recipient_email:
      email_manager.send_email(recipient_email,"Your Transaction Summary", html_content)
  
  if running_type == 'prod':
    dynamo_db_manager = DynamoDBManager(os.getenv('DYNAMODB_TRANSACTIONS_TABLE_NAME'))
    dynamo_db_manager.save_transactions(transactions)
  # return message to confirm processing
  return {
      'statusCode': 200,
      'body': 'Successfully processed transactions and sent summary email.'
  }
