# def load_config():
#     # Assuming your project structure places the .env file at the project root
#   dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
#   print(f'Loading environment variables from: {dotenv_path}')
#   load_dotenv(dotenv_path)

# # Call `load_config` when this module is imported
# load_config()

import os
from dotenv import load_dotenv

# Define a function to determine if the environment is AWS Lambda
def running_on_aws_lambda():
    return os.getenv('AWS_EXECUTION_ENV') is not None

# Load environment variables from .env file when not running on AWS Lambda
if not running_on_aws_lambda():
    # Assuming your project structure places the .env file at the project root
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    print(f'Loading environment variables from: {dotenv_path}')
    load_dotenv(dotenv_path)

# Configuration getters that you use throughout your code
def get_config_value(key, default=None):
    return os.getenv(key, default)

# Example usage within your application:
# DATABASE_URL = get_config_value('DATABASE_URL')
