# transaction_api

# Description
this project use two approach one for a prod environment that use serverless architecture when we have lambdas, s3, api gateway, ses and dynamodb
and for local running, we use the library python-lambda-local and a file named event.json that process the lambda but local

# Architecture
the architecture consists of:
* S3 bucket: to load csv file
* Lambda function: process files and updates dynamodb
* DynamoDB: stores account and transaction tables
* SES: for send email summaries

![architecture drawio (1)](https://github.com/radamanthiss/transaction_api/assets/22681704/271c4b2b-9bba-491a-85b4-c6935795c9a6)


# Requirements
to run this project successfully we need some initial configurations.
- Python 3.9 or above
- AWS CLI configured with access
- Terraform
- An aws account


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
# Description
this project use two approach one for a prod environment that use serverless architecture when we have lambdas, s3, api gateway, ses and dynamodb
and for local running, we use the library python-lambda-local and a file named event.json that process the lambda but local

# Architecture
the architecture consists of:
* S3 bucket: to load csv file
* Lambda function: process files and updates dynamodb
* DynamoDB: stores account and transaction tables
* SES: for send email summaries

![architecture drawio (1)](https://github.com/radamanthiss/transaction_api/assets/22681704/271c4b2b-9bba-491a-85b4-c6935795c9a6)


# Requirements
to run this project successfully we need some initial configurations.
- Python 3.9 or above
- AWS CLI configured with access
- Terraform
- An aws account


# Environment
in this project we can use any environment library, like pipenv or similar i use miniconda to setup the environment with this command
- conda create -n transaction_env python=3.9.18
then for activate this command
- conda activate transaction_env

then we can run the command  to install the package
- pip install -r requirements.txt 

# Running on Local
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
or if you are in the root project route this is the command
- python-lambda-local -f lambda_handler -t 5 src/lambda_function.py event.json

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

## Set environment variables
you have to create .env file in the project root with the variables
* AWS_REGION : us-east-1
* DYNAMODB_TRANSACTIONS_TABLE_NAME: transactions
* DYNAMODB_ACCOUNTS_TABLE_NAME: accounts
* SENDER_EMAIL : ulkevinb@gmail.com   ## For test you can leave all variables without change
* RECIPIENT_EMAIL: 'youremail@example.com'

Ensure that you have configure aws credentials you can use this command
- aws configure
and put the aws credentials like this
- aws_access_key_id = AKIA6ODUZRWNILSVV6UX
- aws_secret_access_key = CNaHauFM6LXaoAB0unKrAUqBtbYqj+AfiTA4pkPP
- region=us-east-1

this can change for your aws account crediental that you can configure in this section
- profile -> security credential -> access key

![Captura de pantalla 2024-03-22 a la(s) 3 02 04 p  m  (2)](https://github.com/radamanthiss/transaction_api/assets/22681704/617d44e5-e31f-4b73-8b8e-8f7cacc846d6)

# AWS Deployment
Once you have configure aws credential you can deploy the serverless services
1. Initialize terraform
```terraform init```

2. Generate the plan
```terraform plan```

3. Apply terraform config
```terraform apply```

then review the plan and confirm with 'yes' the changes

# Sending Test Transactions
Upload a test transaction file to your configured S3 bucket.
The Lambda function should trigger automatically and process the file. In the upload folder in src folder you can find a csv file with information for the testing


# Testing
you can run pytest test/ to run the different test for the project


# Evidence of funcionality AWS
you can see this video with the funcionality for local and prod 
in the bucket in s3 you have to create the uploads folder to put the csv file into this folder

![screenshot-s3 console aws amazon com-2024 03 22-15_14_14](https://github.com/radamanthiss/transaction_api/assets/22681704/d804c4e8-203b-4aef-8eb1-e37d3e122455)

Now in this video you can see how the lambda send the email when a event in this case putObject in s3 when load the file trigger the lambda and this process the info and send the email with SES aws

[screencast-bpconcjcammlapcogcnnelfmaeghhagj-2024.03.22-15_18_18.webm](https://github.com/radamanthiss/transaction_api/assets/22681704/831c771a-f188-46f4-a683-4ebca4e90a82)



# Evidence of funcionality Local

This video is for how works running the lambda in local and using smtp library to send the email.

[screencast-bpconcjcammlapcogcnnelfmaeghhagj-2024.03.22-15_26_46.webm](https://github.com/radamanthiss/transaction_api/assets/22681704/4e4e47b2-ead4-485b-b6cd-1816ff51dd98)