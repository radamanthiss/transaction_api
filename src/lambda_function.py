from collections import defaultdict
import logging
from jinja2 import Template
from util import format_monthly_summaries, read_s3_file, parse_transactions, calculate_balance, calculate_overall_averages, calculate_transactions_by_month
from email_manager import EmailManager
from dynamodb_manager import DynamoDBManager
import os
import config

def get_email(account_id):
  dynamo_db_manager_account = DynamoDBManager(os.getenv('DYNAMODB_ACCOUNTS_TABLE_NAME'))
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
  # Load the Jinja2 template
  email_template_str = """<!DOCTYPE html>
  <html lang="en">
  <head>
      <meta charset="UTF-8">
      <title>Transaction Summary</title>
      <style>
          body {
              font-family: Arial, sans-serif;
              margin: 0;
              padding: 20px;
              color: #333;
          }
          .summary-header {
              background-color: #f0f0f0;
              padding: 10px;
              text-align: center;
          }
      </style>
  </head>
  <body>
      <div class="summary-header">
          <!-- <img src="data:image/png;base64,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" class="logo" alt="Stori Logo" /> -->
          <!-- data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTU0IiBoZWlnaHQ9IjQ4IiB2aWV3Qm94PSIwIDAgMTU0IDQ4IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNNTQuOTc5MiAzNi44MjQxQzU0Ljk3OTIgMzYuMjUzNiA1NS4xMzQ5IDM1LjczNDggNTUuNDk4IDM1LjIxNjFDNTUuODYxIDM0LjY5NzQgNTYuMjc2IDM0LjQzODEgNTYuNzk0NyAzNC40MzgxQzU3LjE1NzggMzQuNDM4MSA1Ny42MjQ2IDM0LjY5NzQgNTguMjQ3MSAzNS4yMTYxQzU4Ljg2OTUgMzUuNzM0OCA1OS44MDMyIDM2LjI1MzYgNjAuOTk2MiAzNi43NzIzQzYyLjE4OTMgMzcuMjkxIDYzLjU4OTggMzcuNTUwMyA2NS4xOTc3IDM3LjU1MDNDNjcuMzI0NCAzNy41NTAzIDY4Ljg4MDYgMzcuMTg3MiA2OS44MTQyIDM2LjQwOTJDNzAuNzQ3OSAzNS42MzExIDcxLjI2NjYgMzQuNjQ1NiA3MS4yNjY2IDMzLjUwNDRDNzEuMjY2NiAzMi4xMDM5IDcwLjc0NzkgMzAuOTYyOCA2OS42NTg2IDMwLjEzMjhDNjguNTY5MyAyOS4zMDI5IDY3LjI3MjYgMjguNjgwNSA2NS43NjgzIDI4LjIxMzZDNjQuMjEyMiAyNy43OTg3IDYyLjcwOCAyNy4zMzE4IDYxLjE1MTggMjYuODEzMUM1OS41OTU3IDI2LjI5NDQgNTguMjk5IDI1LjQxMjYgNTcuMjYxNiAyNC4yMTk2QzU2LjIyNDEgMjMuMDI2NiA1NS42NTM2IDIxLjQxODYgNTUuNjUzNiAxOS40NDc1QzU1LjY1MzYgMTcuMDYxNSA1Ni41MzU0IDE0Ljk4NjYgNTguMjQ3MSAxMy4yMjNDNTkuOTU4OCAxMS40NTk0IDYyLjYwNDIgMTAuNTc3NiA2Ni4xMzE0IDEwLjU3NzZDNjguMzYxOCAxMC41Nzc2IDcwLjQzNjcgMTAuOTQwNyA3Mi4zMDQgMTEuNjE1Qzc0LjE3MTQgMTIuMjg5NCA3NS4xMDUgMTMuMDY3NCA3NS4xMDUgMTMuOTQ5MkM3NS4xMDUgMTQuNDY3OSA3NC44OTc1IDE1LjAzODUgNzQuNDgyNiAxNS42NjFDNzQuMDY3NiAxNi4yODM0IDczLjYwMDggMTYuNTk0NiA3Mi45NzgzIDE2LjU5NDZDNzIuODIyNyAxNi41OTQ2IDcxLjk5MjggMTYuMjgzNCA3MC41NDA0IDE1LjY2MUM2OS4wODggMTUuMDM4NSA2Ny42MzU3IDE0LjcyNzMgNjYuMTgzMyAxNC43MjczQzY0LjIxMjIgMTQuNzI3MyA2Mi43NTk4IDE1LjE5NDEgNjEuODI2MiAxNi4xMjc4QzYwLjg5MjUgMTcuMDYxNSA2MC4zNzM4IDE4LjA5ODkgNjAuMzczOCAxOS4yNEM2MC4zNzM4IDIwLjQzMyA2MC44OTI1IDIxLjM2NjcgNjEuOTgxOCAyMi4wOTI5QzYzLjAxOTIgMjIuNzY3MiA2NC4zNjc4IDIzLjMzNzggNjUuOTIzOSAyMy43MDA5QzY3LjQ4IDI0LjA2NCA2OS4wMzYyIDI0LjU4MjcgNzAuNTQwNCAyNS4xMDE0QzcyLjA5NjUgMjUuNjcyIDczLjM5MzMgMjYuNjA1NiA3NC40MzA3IDI3Ljk1NDNDNzUuNDY4MSAyOS4zMDI5IDc2LjAzODcgMzEuMDY2NSA3Ni4wMzg3IDMzLjE5MzJDNzYuMDM4NyAzNS43ODY3IDc1LjEwNSAzNy44NjE1IDczLjIzNzcgMzkuMzY1OEM3MS4zNzAzIDQwLjg3IDY4LjcyNDkgNDEuNjQ4MSA2NS40MDUyIDQxLjY0ODFDNjIuNTAwNSA0MS42NDgxIDYwLjA2MjYgNDEuMTI5NCA1Ny45ODc3IDQwLjA5MkM1NS45NjQ4IDM5LjA1NDYgNTQuOTc5MiAzNy45NjUzIDU0Ljk3OTIgMzYuODI0MVoiIGZpbGw9IiMzODQ5NjciLz4KPHBhdGggZD0iTTgwLjEzNjQgMzEuNTMzM1YzLjQxOTQ3QzgwLjEzNjQgMi45MDA3NyA4MC4zOTU3IDIuNDg1OCA4MC45NjYzIDIuMTIyNzFDODEuNTM2OSAxLjc1OTYyIDgyLjEwNzQgMS42MDQgODIuNzI5OSAxLjYwNEM4My40MDQyIDEuNjA0IDg0LjAyNjYgMS44MTE0OSA4NC41OTcyIDIuMTIyNzFDODUuMTY3OCAyLjQ4NTggODUuNDI3MSAyLjkwMDc3IDg1LjQyNzEgMy40MTk0N1YxMC44ODg4SDkzLjQ2NzFDOTMuOTMzOSAxMC44ODg4IDk0LjI5NyAxMS4wOTYzIDk0LjYwODIgMTEuNTExM0M5NC45MTk1IDExLjkyNjIgOTUuMDc1MSAxMi40NDQ5IDk1LjA3NTEgMTIuOTYzN0M5NS4wNzUxIDEzLjUzNDIgOTQuOTE5NSAxNC4wMDExIDk0LjYwODIgMTQuNDE2Qzk0LjI5NyAxNC44MzEgOTMuOTMzOSAxNS4wMzg1IDkzLjQ2NzEgMTUuMDM4NUg4NS40MjcxVjMxLjM3NzdDODUuNDI3MSAzMy4xOTMyIDg1Ljg0MjEgMzQuNDg5OSA4Ni42MjAyIDM1LjIxNjFDODcuMzk4MiAzNS45NDIzIDg4Ljc5ODcgMzYuMzA1NCA5MC43MTc5IDM2LjMwNTRIOTIuNjg5QzkzLjQxNTIgMzYuMzA1NCA5My45ODU4IDM2LjUxMjkgOTQuNDAwOCAzNi45Nzk3Qzk0LjgxNTcgMzcuNDQ2NiA5NS4wMjMyIDM4LjAxNzEgOTUuMDIzMiAzOC42OTE0Qzk1LjAyMzIgMzkuMzY1OCA5NC44MTU3IDM5LjkzNjMgOTQuNDAwOCA0MC40MDMyQzkzLjk4NTggNDAuODcgOTMuNDE1MiA0MS4xMjk0IDkyLjc0MDkgNDEuMTI5NEg5MC43Njk4QzgzLjY2MzUgNDEuMTgxMiA4MC4xMzY0IDM3Ljk2NTMgODAuMTM2NCAzMS41MzMzWiIgZmlsbD0iIzM4NDk2NyIvPgo8cGF0aCBkPSJNOTYuOTQyNCAyOS4zMDNWMjIuNzY3M0M5Ni45NDI0IDE5LjQ5OTUgOTguMTg3MyAxNi42NDY2IDEwMC42NzcgMTQuMjA4N0MxMDMuMTY3IDExLjc3MDggMTA2LjEyMyAxMC41MjU5IDEwOS40OTUgMTAuNTI1OUMxMTIuODY3IDEwLjUyNTkgMTE1Ljg3NSAxMS43MTg5IDExOC4zNjUgMTQuMTU2OEMxMjAuODU1IDE2LjU5NDcgMTIyLjE1MSAxOS40NDc2IDEyMi4xNTEgMjIuNzY3M1YyOS4zMDNDMTIyLjE1MSAzMi41MTkgMTIwLjkwNyAzNS40MjM3IDExOC4zNjUgMzcuOTEzNUMxMTUuODIzIDQwLjQwMzMgMTEyLjg2NyA0MS43MDAxIDEwOS41NDcgNDEuNzAwMUMxMDYuMTc1IDQxLjcwMDEgMTAzLjI3MSA0MC40NTUyIDEwMC43MjkgMzcuOTY1NEM5OC4xODczIDM1LjQyMzcgOTYuOTQyNCAzMi41NzA5IDk2Ljk0MjQgMjkuMzAzWk0xMDIuMjMzIDI5LjI1MTFDMTAyLjIzMyAzMS4yMjIyIDEwMi45NTkgMzIuOTg1OCAxMDQuNDEyIDM0LjU0MTlDMTA1Ljg2NCAzNi4wNDYyIDEwNy41NzYgMzYuODI0MiAxMDkuNDk1IDM2LjgyNDJDMTExLjUxOCAzNi44MjQyIDExMy4yMyAzNi4wNDYyIDExNC42ODIgMzQuNDkwMUMxMTYuMTM0IDMyLjkzNCAxMTYuODYxIDMxLjIyMjIgMTE2Ljg2MSAyOS4yNTExVjIyLjgxOTJDMTE2Ljg2MSAyMC45IDExNi4xMzQgMTkuMTg4MyAxMTQuNjgyIDE3LjY4NEMxMTMuMjMgMTYuMTc5OCAxMTEuNTE4IDE1LjQwMTcgMTA5LjQ5NSAxNS40MDE3QzEwNy40NzIgMTUuNDAxNyAxMDUuNzYgMTYuMTc5OCAxMDQuMzYgMTcuNjg0QzEwMi45MDcgMTkuMTg4MyAxMDIuMjMzIDIwLjkgMTAyLjIzMyAyMi44MTkyVjI5LjI1MTFaIiBmaWxsPSIjMzg0OTY3Ii8+CjxwYXRoIGQ9Ik0xMjcuMTMxIDM5LjI2MjJWMTIuNzU2M0MxMjcuMTMxIDEyLjE4NTcgMTI3LjM5IDExLjc3MDggMTI3Ljg1NyAxMS40MDc3QzEyOC4zMjQgMTEuMDQ0NiAxMjguOTk4IDEwLjg4OSAxMjkuNzI1IDEwLjg4OUMxMzAuMzk5IDEwLjg4OSAxMzAuOTcgMTEuMDQ0NiAxMzEuNDM2IDExLjQwNzdDMTMxLjkwMyAxMS43NzA4IDEzMi4xNjMgMTIuMTg1NyAxMzIuMTYzIDEyLjc1NjNWMTUuODE2N0MxMzIuOTQxIDE0LjM2NDMgMTM0LjAzIDEzLjExOTQgMTM1LjUzNCAxMi4wODJDMTM3LjAzOCAxMS4wNDQ2IDEzOC42OTggMTAuNTI1OSAxNDAuNTE0IDEwLjUyNTlIMTQyLjY5MkMxNDMuMjYzIDEwLjUyNTkgMTQzLjczIDEwLjc4NTIgMTQ0LjE0NSAxMS4yNTIxQzE0NC41NiAxMS43NzA4IDE0NC43NjcgMTIuMzQxMyAxNDQuNzY3IDEyLjk2MzhDMTQ0Ljc2NyAxMy41ODYyIDE0NC41NiAxNC4xNTY4IDE0NC4xNDUgMTQuNjIzN0MxNDMuNzMgMTUuMDkwNSAxNDMuMjYzIDE1LjM0OTggMTQyLjY5MiAxNS4zNDk4SDE0MC41MTRDMTM4LjMzNSAxNS4zNDk4IDEzNi40NjggMTYuMjMxNiAxMzQuODYgMTcuOTQzNEMxMzMuMjUyIDE5LjcwNyAxMzIuNDIyIDIxLjkzNzQgMTMyLjQyMiAyNC42ODY1VjM5LjIxMDNDMTMyLjQyMiAzOS42NzcxIDEzMi4xNjMgNDAuMDkyMSAxMzEuNjQ0IDQwLjUwNzFDMTMxLjEyNSA0MC45MjIgMTMwLjUwMyA0MS4xMjk1IDEyOS43NzcgNDEuMTI5NUMxMjkuMDUgNDEuMTI5NSAxMjguNDI4IDQwLjkyMiAxMjcuOTA5IDQwLjU1ODlDMTI3LjMzOSA0MC4xOTU4IDEyNy4xMzEgMzkuNzI5IDEyNy4xMzEgMzkuMjYyMloiIGZpbGw9IiMzODQ5NjciLz4KPHBhdGggZD0iTTE0OC40NSA2LjY4NzQzQzE0Ny43NzYgNi4wNjQ5OCAxNDcuNDY0IDUuMzM4OCAxNDcuNDY0IDQuNTYwNzRDMTQ3LjQ2NCAzLjczMDgxIDE0Ny43NzYgMy4wNTY0OSAxNDguMzk4IDIuNDM0MDVDMTQ5LjAyIDEuODYzNDcgMTQ5Ljc5OSAxLjU1MjI1IDE1MC43ODQgMS41NTIyNUMxNTEuNjY2IDEuNTUyMjUgMTUyLjQ0NCAxLjg2MzQ3IDE1My4wNjYgMi40MzQwNUMxNTMuNjg5IDMuMDA0NjIgMTU0IDMuNzMwODEgMTU0IDQuNTYwNzRDMTU0IDUuMzkwNjcgMTUzLjY4OSA2LjA2NDk4IDE1My4wNjYgNi42ODc0M0MxNTIuNDQ0IDcuMzA5ODggMTUxLjY2NiA3LjYyMTEgMTUwLjc4NCA3LjYyMTFDMTQ5LjkwMiA3LjYyMTEgMTQ5LjEyNCA3LjMwOTg4IDE0OC40NSA2LjY4NzQzWk0xNDguMTM5IDM5LjI2MjFWMTIuNzU2M0MxNDguMTM5IDEyLjE4NTcgMTQ4LjM5OCAxMS43NzA3IDE0OC45MTcgMTEuNDA3NkMxNDkuNDM1IDExLjA0NDYgMTUwLjA1OCAxMC44ODg5IDE1MC43ODQgMTAuODg4OUMxNTEuNTYyIDEwLjg4ODkgMTUyLjE4NSAxMS4wNDQ2IDE1Mi43MDMgMTEuNDA3NkMxNTMuMjIyIDExLjc3MDcgMTUzLjQ4MSAxMi4xODU3IDE1My40ODEgMTIuNzU2M1YzOS4yNjIxQzE1My40ODEgMzkuNzI5IDE1My4yMjIgNDAuMTQzOSAxNTIuNzAzIDQwLjU1ODlDMTUyLjE4NSA0MC45NzM5IDE1MS41NjIgNDEuMTgxMyAxNTAuODM2IDQxLjE4MTNDMTUwLjExIDQxLjE4MTMgMTQ5LjQ4NyA0MC45NzM5IDE0OC45NjkgNDAuNjEwOEMxNDguMzk4IDQwLjE5NTggMTQ4LjEzOSAzOS43MjkgMTQ4LjEzOSAzOS4yNjIxWiIgZmlsbD0iIzM4NDk2NyIvPgo8cGF0aCBkPSJNMjguNjI4OSAzLjYyNzAyQzI5Ljc3MDEgNi41ODM2NCAyOC4zMTc3IDkuOTU1MjIgMjUuMzYxMSAxMS4wOTY0TDguNDUxMjcgMTcuNzg3N0M1LjQ5NDY1IDE4LjkyODggMi4xNzQ5MyAxNy40NzY1IDAuOTgxOTExIDE0LjUxOThDLTAuMjExMTExIDExLjU2MzIgMS4yOTMxMyA4LjE5MTYzIDQuMjQ5NzYgNy4wNTA0N0wyMS4xNTk2IDAuNDExMDQzQzI0LjExNjIgLTAuNzgxOTc5IDI3LjQ4NzggMC43MjIyNjYgMjguNjI4OSAzLjYyNzAyWiIgZmlsbD0iIzAwRjVFQiIvPgo8cGF0aCBkPSJNMTIuNTQ5MSA0My45MzA1QzExLjQwNzkgNDAuOTczOCAxMi44NjAzIDM3LjYwMjMgMTUuODE2OSAzNi40NjExTDMyLjcyNjcgMjkuODIxN0MzNS42ODM0IDI4LjY4MDUgMzkuMDU1IDMwLjEzMjkgNDAuMTk2MSAzMy4wODk1QzQxLjMzNzMgMzYuMDQ2MSAzOS44ODQ5IDM5LjQxNzcgMzYuOTI4MyA0MC41NTg5TDIwLjAxODUgNDcuMTQ2NEMxNy4xMTM3IDQ4LjMzOTUgMTMuNzQyMSA0Ni44MzUyIDEyLjU0OTEgNDMuOTMwNVoiIGZpbGw9IiNGRjhDRDkiLz4KPHBhdGggZD0iTTAuOTgxODM5IDE0LjUxOTlDMi4xMjI5OSAxNy40NzY1IDUuNDk0NTggMTguOTI4OSA4LjQ1MTIgMTcuNzg3N0w5Ljg1MTcgMTcuMjY5QzkuNjQ0MjIgMTYuOTA1OSA5LjQzNjc0IDE2LjQ5MDkgOS4yODExMyAxNi4wNzZDNy4yMDYzMSAxMC43ODUyIDkuNzk5ODMgNC44NzE5NCAxNS4wMzg4IDIuNzk3MTJMNC4yNDk2OCA3LjA1MDVDMS4yOTMwNiA4LjE5MTY2IC0wLjE1OTMxMyAxMS41NjMyIDAuOTgxODM5IDE0LjUxOTlaIiBmaWxsPSIjNzhBQ0Y4Ii8+CjxwYXRoIGQ9Ik0zMS45NDg3IDMxLjUzMzVDMzQuMDIzNSAzNi43NzI0IDMxLjQzIDQyLjczNzYgMjYuMTkxIDQ0Ljc2MDVMMzYuOTgwMSA0MC41MDcxQzM5LjkzNjcgMzkuMzY2IDQxLjM4OTEgMzUuOTk0NCA0MC4yNDggMzMuMDM3OEMzOS4xMDY4IDMwLjA4MTEgMzUuNzM1MiAyOC42Mjg4IDMyLjc3ODYgMjkuNzY5OUwzMS4zNzgxIDMwLjI4ODZDMzEuNTg1NiAzMC43MDM2IDMxLjc5MzEgMzEuMTE4NiAzMS45NDg3IDMxLjUzMzVaIiBmaWxsPSIjQkE2QkVCIi8+CjxwYXRoIGQ9Ik00MC4wOTIzIDI3LjUzOTNDMzguNjkxOCAyNC42ODY0IDM3LjE4NzYgMjMuMjg1OSAzNC42OTc4IDIxLjc4MTdDMzMuMjk3MyAyMC45NTE3IDI3LjU5MTUgMTkuMTM2MyAyMS41NzQ1IDE3LjMyMDhDMTQuNTcyIDE1LjE0MjIgNi42ODc2OCAxMi42NTI0IDUuMTgzNDMgMTEuOTI2M0MyLjMzMDU1IDEwLjYyOTUgMi4wNzEyIDguOTE3NzYgMy4wMDQ4NyA3Ljc3NjYxQy0wLjI2Mjk3NCA5Ljc5OTU2IC0wLjgzMzU1IDE2LjA3NTkgMS4xMzc1MyAyMC4xMjE4QzIuNTM4MDQgMjIuOTc0NyA0LjA0MjI4IDI0LjM3NTIgNi41MzIwNyAyNS44Nzk0QzcuOTMyNTcgMjYuNzA5NCAxMy42MzgzIDI4LjUyNDggMTkuNjU1MyAzMC4zNDAzQzI2LjY1NzggMzIuNTE4OSAzNC41NDIyIDM1LjA2MDUgMzYuMDQ2NCAzNS43MzQ4QzM4Ljg5OTMgMzcuMDMxNiAzOS4xNTg2IDM4Ljc0MzMgMzguMjI1IDM5Ljg4NDVDNDEuNDkyOCAzNy44NjE1IDQyLjA2MzQgMzEuNTg1MiA0MC4wOTIzIDI3LjUzOTNaIiBmaWxsPSIjQTlGRjk1Ii8+Cjwvc3ZnPgo= -->
          <img src='https://finnovating.s3.eu-central-1.amazonaws.com/companies/company_26535/main_logo_26535.png' alt="logo"/>
          <h1>Transaction Summary</h1>
      </div>
      <p>Total Balance: {{total_balance}}</p>
      <p>Average credit amount: {{average_credit}}</p>
      <p>Average debit amount: {{average_debit}}</p>
      {{monthly_summaries}}

      <!-- Add more placeholders and dynamic content as needed -->
  </body>
  </html>
  """
  template = Template(email_template_str)
  # Create an instance of the DynamoDBManager
  dynamo_db_manager = DynamoDBManager(os.getenv('DYNAMODB_TRANSACTIONS_TABLE_NAME'))  
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
