variable "aws_region" {
  description = "The AWS region to deploy resources into"
  type        = string
  default     = "us-east-1" # You can set a default region. This line is optional and can be omitted.
}

variable "aws_account_id" {
  description = "The AWS account ID"
  type        = string
  default     = "992382389658"
}