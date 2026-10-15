locals {
  mcp_token_secret_name = "${local.prefix}-mcp-bearer-token"
  mcp_authorizer_name   = "${local.prefix}-mcp-authorizer"
}

resource "aws_kms_key" "mcp_token" {
  description             = "Encrypts the ${local.prefix} MCP bearer token secret"
  enable_key_rotation     = true
  deletion_window_in_days = 30

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_kms_alias" "mcp_token" {
  name          = "alias/${local.mcp_token_secret_name}"
  target_key_id = aws_kms_key.mcp_token.key_id
}

# The secret value is set out of band (aws secretsmanager put-secret-value), never in Terraform.
#checkov:skip=CKV2_AWS_57:Shared bearer token is rotated manually (spec 007 out of scope)
resource "aws_secretsmanager_secret" "mcp_token" {
  name        = local.mcp_token_secret_name
  description = "Shared bearer token for the ${local.prefix} MCP endpoints"
  kms_key_id  = aws_kms_key.mcp_token.arn
}

resource "aws_cloudwatch_log_group" "mcp_authorizer" {
  name              = "/aws/lambda/${local.mcp_authorizer_name}"
  retention_in_days = 14
}

data "aws_iam_policy_document" "mcp_authorizer_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "mcp_authorizer" {
  name               = local.mcp_authorizer_name
  assume_role_policy = data.aws_iam_policy_document.mcp_authorizer_assume.json
}

data "aws_iam_policy_document" "mcp_authorizer" {
  statement {
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.mcp_authorizer.arn}:*"]
  }

  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.mcp_token.arn]
  }

  statement {
    actions   = ["kms:Decrypt"]
    resources = [aws_kms_key.mcp_token.arn]
  }
}

resource "aws_iam_role_policy" "mcp_authorizer" {
  name   = "authorizer"
  role   = aws_iam_role.mcp_authorizer.id
  policy = data.aws_iam_policy_document.mcp_authorizer.json
}

data "archive_file" "mcp_authorizer" {
  type        = "zip"
  source_dir  = "${path.root}/../src/mcp_authorizer"
  output_path = "${path.module}/modules/lambda_endpoint/build/${local.mcp_authorizer_name}.zip"
}

resource "aws_lambda_function" "mcp_authorizer" {
  function_name    = local.mcp_authorizer_name
  role             = aws_iam_role.mcp_authorizer.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  timeout          = 5
  memory_size      = 128
  filename         = data.archive_file.mcp_authorizer.output_path
  source_code_hash = data.archive_file.mcp_authorizer.output_base64sha256

  environment {
    variables = {
      TOKEN_SECRET_ARN = aws_secretsmanager_secret.mcp_token.arn
      LOG_LEVEL        = "INFO"
    }
  }

  depends_on = [aws_cloudwatch_log_group.mcp_authorizer]
}

resource "aws_apigatewayv2_authorizer" "mcp_bearer" {
  api_id                            = aws_apigatewayv2_api.this.id
  name                              = "${local.prefix}-mcp-bearer"
  authorizer_type                   = "REQUEST"
  authorizer_uri                    = aws_lambda_function.mcp_authorizer.invoke_arn
  authorizer_payload_format_version = "2.0"
  enable_simple_responses           = true
  identity_sources                  = ["$request.header.Authorization"]
  authorizer_result_ttl_in_seconds  = 300
}

resource "aws_lambda_permission" "mcp_authorizer" {
  statement_id  = "AllowAPIGatewayInvokeAuthorizer"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mcp_authorizer.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/authorizers/${aws_apigatewayv2_authorizer.mcp_bearer.id}"
}
