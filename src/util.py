from collections import defaultdict
import locale
import boto3
from decimal import Decimal
from datetime import datetime
import csv
from typing import List, Dict
import config

locale.setlocale(locale.LC_TIME, 'es_ES')

def read_s3_file(bucket: str, key: str) -> str:
    """
    Reads a file from an S3 bucket.

    Parameters
    ----------
    bucket : str
        The name of the S3 bucket.
    key : str
        The key of the file in the S3 bucket.

    Returns
    -------
    str
        The content of the file as a string.
    """
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=key)
    print('bucket:____', bucket)  # For debugging
    print('key:____', key)  # For debugging
    print("obj['Body']:", obj['Body'])  # For debugging
    return obj['Body'].read().decode('utf-8')

def parse_transactions(csv_content: str) -> List[Dict]:
    """
    Parses CSV content into a list of transaction dictionaries.

    Parameters
    ----------
    csv_content : str
        CSV content as a string.

    Returns
    -------
    List[Dict]
        A list of transactions represented as dictionaries.
    """
    if csv_content.startswith('\ufeff'):
        csv_content = csv_content[1:]
    transactions = []
    reader = csv.DictReader(csv_content.splitlines(),delimiter=';')
    for row in reader:
        
        date_str = row['Date'].title()  # Convert 'jul' to 'Jul' to match %b expectation
        try:
            date_parsed = datetime.strptime(date_str, '%b-%d')
            current_year = datetime.now().year
            date_parsed = date_parsed.replace(year=current_year)
        except ValueError as e:
            print(f"Error parsing date {date_str}: {e}")
            continue
        transaction = {
            'id': row['Id'],
            'accountId': row['AccountId'],
            'date': date_parsed,
            'transaction': Decimal(row['Transaction'])
        }
        transactions.append(transaction)
    return transactions

def calculate_balance(transactions: List[Dict]) -> Decimal:
    """
    Calculates the total balance from a list of transactions.

    Parameters
    ----------
    transactions : List[Dict]
        A list of transactions.

    Returns
    -------
    Decimal
        The total balance.
    """
    total_balance = sum([transaction['transaction'] for transaction in transactions])
    return total_balance

def calculate_overall_averages(transactions):
    """
    Calculates monthly averages for credit and debit transactions.

    Parameters
    ----------
    transactions : List[Dict]
        A list of transactions.

    Returns
    -------
    Dict
        A dictionary containing monthly averages of credit and debit transactions.
    """
    monthly_credits = defaultdict(list)
    monthly_debits = defaultdict(list)

    # for transaction in transactions:
    #     month = datetime.strptime(transaction['date'].strftime('%B'), '%B').strftime('%B')
    #     if transaction['transaction'] > 0:
    #         monthly_credits[month].append(transaction['transaction'])
    #     else:
    #         monthly_debits[month].append(transaction['transaction'])

    # monthly_averages = {
    #     'credit': {month: sum(trans) / len(trans) for month, trans in monthly_credits.items()},
    #     'debit': {month: sum(trans) / len(trans) for month, trans in monthly_debits.items()}
    # }
    credits = [transaction['transaction'] for transaction in transactions if transaction['transaction'] > 0]
    debits = [transaction['transaction'] for transaction in transactions if transaction['transaction'] < 0]

    average_credit = sum(credits) / len(credits) if credits else 0
    average_debit = sum(debits) / len(debits) if debits else 0

    return {
        'average_credit': average_credit,
        'average_debit': average_debit
    }

def calculate_transactions_by_month(transactions: List[Dict]) -> Dict[str, int]:
    """
    Counts the number of transactions per month.

    Parameters
    ----------
    transactions : List[Dict]
        A list of transactions.

    Returns
    -------
    Dict[str, int]
        A dictionary with month names as keys and transaction counts as values.
    """
    transactions_by_month = {}
    for transaction in transactions:
        month = transaction['date'].strftime('%B')
        transactions_by_month[month] = transactions_by_month.get(month, 0) + 1
        # month = date.strftime('%B')

        # if month in transactions_by_month:
        #     transactions_by_month[month] += 1
        # else:
        #     transactions_by_month[month] = 1
        
    return transactions_by_month

def format_monthly_summaries(transactions_by_month):
    """Generate a formatted string for the monthly summaries."""
    formatted_summary = ""
    for month, count in transactions_by_month.items():
        formatted_summary += f"<p>Number of transactions in {month}: {count}<br></p>"
    return formatted_summary


