# transaction_api

# Description
this project use two approach one for a prod environment that use serverless architecture when we have lambdas, s3, api gateway, ses and dynamodb
and for local running, we use the library python-lambda-local and a file named event.json that process the lambda but local

# Requirements
to run this project successfully we need some initial configurations.
- Python 3.9 or above
- AWS CLI
- Terraform


# Environment
in this project we can use any environment library, like pipenv or similar i use miniconda to setup the environment with this command
- conda create -n transaction_env python=3.9.18
then for activate this command
- conda activate transaction_env

then we can run the command pip install -r requirements.txt to install the package

# RUNNING ON LOCAL
First you need to change the .env file with your variables for smtp 
```
SMTP_SERVER='smtp.gmail.com'
SMTP_PORT='587'
SMTP_USER='ulkevinb@gmail.com'
SMTP_PASSWORD='frga vopv ieua eqai'
DYNAMODB_TRANSACTIONS_TABLE_NAME = 'transactions'
DYNAMODB_ACCOUNTS_TABLE_NAME = 'accounts'
SENDER_EMAIL = 'ulkevinb@gmail.com'
AWS_REGION = 'us-east-1'
RECIPIENT_EMAIL='put your email'
```

for testing only change the recipient_email variable and then you can run the lambda_function with this command in the route of src folder
- cd src
- python-lambda-local -f lambda_handler -t 5 lambda_function.py ../event.json

this is the stucture of event.json don't change any in the json if you want to test prod locally change the variable running_type: "prod" or remove this line, but for this testing is necessary that you have all the serverless deployment in aws account
```json
{
  "running_type": "local",
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "stori-challenge-transaction-bucket"
        },
        "object": {
          "key": "uploads/stori_challenge_123.csv"
        }
      }
    }
  ]
}
```