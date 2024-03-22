from datetime import datetime
import locale
from moto import mock_aws
import boto3
import pytest
from decimal import Decimal

from src.util import read_s3_file, parse_transactions, calculate_balance, calculate_overall_averages, calculate_transactions_by_month, format_monthly_summaries

locale.setlocale(locale.LC_TIME, 'es_ES')

@pytest.fixture
def mock_s3_bucket():
  with mock_aws():
    s3 = boto3.client('s3', region_name='us-east-1')
    bucket_name = 'stori-challenge-transaction-bucket'
    s3.create_bucket(Bucket=bucket_name)
    # s3.put_object(Bucket='stori-challenge-transaction-bucket', Key='uploads/stori_challenge_123.csv', Body="Id;AccountId;Date;Transaction\n1;1;jul-23;10.1\n2;1;jul-23;-8.2")
    yield bucket_name

@pytest.fixture
def mock_csv_content():
  csv_content = 'Id;AccountId;Date;Transaction\n1;1;jul-23;+10.1\n2;1;jul-23;-8.2'
  return csv_content

def test_read_s3_file(mock_s3_bucket, mock_csv_content):
  """Test reading a file from S3."""
  bucket_name = mock_s3_bucket
  file_key = 'uploads/stori_challenge_123.csv'
  s3 = boto3.client('s3', region_name='us-east-1')
  s3.put_object(Bucket=bucket_name, Key=file_key, Body=mock_csv_content)

  file_content = read_s3_file(bucket_name, file_key)
  assert file_content == mock_csv_content
  
  
def test_parse_transactions():
  """Test parsing transactions from a CSV string."""
  csv_content = 'Id;AccountId;Date;Transaction\n1;1;jul-23;+10.1\n2;1;jul-23;-8.2'
  transactions = parse_transactions(csv_content)
  assert len(transactions) == 2
  assert transactions[0]['date'].strftime('%b-%d') == 'jul-23'
  
def test_calculate_balance():
  """Test calculating the balance from a list of transactions."""
  transactions = [
    {'id': '1', 'accountId': '1', 'date': 'jul-23', 'transaction': Decimal('10.1')},
    {'id': '2', 'accountId': '1', 'date': 'jul-23', 'transaction': Decimal('-8.2')}
  ]
  balance = calculate_balance(transactions)
  assert balance == Decimal('1.9')


def test_calculate_overall_averages():
  """Test calculating the overall averages from a list of transactions."""
  transactions = [
    {'id': '1', 'accountId': '1', 'date': datetime.now(), 'transaction': Decimal('10.1')},
    {'id': '2', 'accountId': '1', 'date': datetime.now(), 'transaction': Decimal('-8.2')}
  ]
  averages = calculate_overall_averages(transactions)
  assert averages == {'average_credit': Decimal('10.1'), 'average_debit': Decimal('-8.2')}


def test_calculate_transactions_by_month():
  """Test calculating the transactions by month from a list of transactions."""
  transactions = [
    {'id': '1', 'accountId': '1', 'date': datetime(1900, 7, 23), 'transaction': Decimal('10.1')},
    {'id': '2', 'accountId': '1', 'date': datetime(1900, 7, 23), 'transaction': Decimal('-8.2')}
  ]
  transactions_by_month = calculate_transactions_by_month(transactions)
  assert transactions_by_month == {'julio':2}
  
def test_format_monthly_summaries():
  """Test formatting the monthly summaries into an HTML string."""
  transactions_by_month = {'Jul': 2}
  html = format_monthly_summaries(transactions_by_month)
  assert html == '<p>Number of transactions in Jul: 2<br></p>'
  