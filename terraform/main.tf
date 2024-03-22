provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "transaction_bucket" {
  bucket = "stori-challenge-transaction-bucket"
}

# iam role for lambda execution
resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Sid = ""
      }
    ]
  })

}

# iam role for lambda execution
resource "aws_iam_role" "lambda_account" {
  name = "lambda_account"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Sid = ""
      }
    ]
  })

}

#lambda function for processing transacitons

resource "aws_lambda_function" "process_transactions" {
  function_name    = "process_transactions"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  filename         = "../src/lambda_function.zip"
  source_code_hash = filebase64sha256("../src/lambda_function.py")
  timeout          = 35
  environment {
    variables = {
      bucket                           = aws_s3_bucket.transaction_bucket.bucket
      DYNAMODB_TRANSACTIONS_TABLE_NAME = aws_dynamodb_table.transactions.name
      DYNAMODB_ACCOUNTS_TABLE_NAME     = aws_dynamodb_table.accounts.name
      SENDER_EMAIL                     = aws_ses_email_identity.email_identity.email
      TEMPLATE_PATH                    = "email_template.html"
    }
  }
}

# lambda function for create account
resource "aws_lambda_function" "create_account" {
  function_name    = "create_account"
  role             = aws_iam_role.lambda_account.arn
  handler          = "lambda_account.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("../src/lambda_account.py")
  filename         = "../src/lambda_account.zip"
  timeout          = 35
  environment {
    variables = {
      DYNAMODB_ACCOUNTS_TABLE_NAME = aws_dynamodb_table.accounts.name
    }
  }
}

# dynamodb table for storing transactions
resource "aws_dynamodb_table" "transactions" {
  name           = "transactions"
  billing_mode   = "PROVISIONED"
  hash_key       = "id"
  read_capacity  = 5
  write_capacity = 5

  attribute {
    name = "id"
    type = "S"
  }
}

# dynamo table for storing accounts
resource "aws_dynamodb_table" "accounts" {
  name           = "accounts"
  billing_mode   = "PROVISIONED"
  hash_key       = "id"
  read_capacity  = 5
  write_capacity = 5

  attribute {
    name = "id"
    type = "S"
  }
}

# ses email for notification
resource "aws_ses_email_identity" "email_identity" {
  email = "ulkevinb@gmail.com"
}

resource "aws_lambda_permission" "allow_s3_invocation" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_transactions.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.transaction_bucket.arn

}

# attach s3 bucket notification to lambda function
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.transaction_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.process_transactions.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/"
    filter_suffix       = ".csv"
  }
  depends_on = [aws_lambda_permission.allow_s3_invocation]
}

# IAM policy to allow Lambda function to access S3, DynamoDB, and SES
resource "aws_iam_policy" "lambda_policy" {
  name = "lambda_policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ],
        Effect = "Allow",
        Resource = [
          "${aws_s3_bucket.transaction_bucket.arn}",
          "${aws_s3_bucket.transaction_bucket.arn}/*"
        ]
      },
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:Update*",
          "dynamodb:Delete*",
          "dynamodb:Scan",
          "dynamodb:Query"
        ],
        Effect = "Allow",
        Resource = [
          "arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/accounts",
          "arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/transactions"
        ]
      },
      {
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_dynamodb_access" {
  name = "lambda_dynamodb_access"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Update*",
          "dynamodb:BatchWriteItem",
          "dynamodb:Delete*",
          "dynamodb:Scan",
          "dynamodb:Query"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:dynamodb:${var.aws_region}:${var.aws_account_id}:table/Accounts"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_policy_attachment" {
  role       = aws_iam_role.lambda_account.name
  policy_arn = aws_iam_policy.lambda_dynamodb_access.arn
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn

}

data "aws_iam_policy_document" "lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_account.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_role_policy_attachment" "lambda_function_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}
