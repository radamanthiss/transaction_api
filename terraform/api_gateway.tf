resource "aws_api_gateway_rest_api" "AccountsApi" {
  name        = "AccountsApi"
  description = "This is the API for the Accounts service"
}

resource "aws_api_gateway_resource" "account" {
  rest_api_id = aws_api_gateway_rest_api.AccountsApi.id
  parent_id   = aws_api_gateway_rest_api.AccountsApi.root_resource_id
  path_part   = "account"
}

resource "aws_api_gateway_method" "account_post" {
  rest_api_id   = aws_api_gateway_rest_api.AccountsApi.id
  resource_id   = aws_api_gateway_resource.account.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "account_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.AccountsApi.id
  resource_id = aws_api_gateway_method.account_post.resource_id
  http_method = "${aws_api_gateway_method.account_post.http_method}"
  integration_http_method = "POST"
  type        = "AWS_PROXY"
  uri         = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.create_account.arn}/invocations"
}

resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on  = [aws_api_gateway_integration.account_post_integration]
  rest_api_id = aws_api_gateway_rest_api.AccountsApi.id
  stage_name  = "v1"
}


resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_account.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.AccountsApi.execution_arn}/*/POST/account"
}

output "create_account_api_endpoint" {
  value = aws_api_gateway_deployment.api_deployment.invoke_url
}
