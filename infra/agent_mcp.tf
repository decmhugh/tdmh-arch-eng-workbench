locals {
  agent_mcp_session_table_name = "${local.prefix}-agent-mcp-sessions"
  agent_mcp_session_key_alias  = "alias/${local.prefix}-agent-mcp-sessions"
}

resource "aws_kms_key" "agent_mcp_sessions" {
  description             = "Encrypts the ${local.prefix} Agent MCP session table"
  enable_key_rotation     = true
  deletion_window_in_days = 30

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_kms_alias" "agent_mcp_sessions" {
  name          = local.agent_mcp_session_key_alias
  target_key_id = aws_kms_key.agent_mcp_sessions.key_id
}

resource "aws_dynamodb_table" "agent_mcp_sessions" {
  name         = local.agent_mcp_session_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "session_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.agent_mcp_sessions.arn
  }
}

data "aws_iam_policy_document" "agent_mcp" {
  source_policy_documents = [data.aws_iam_policy_document.agent_invoke.json]

  statement {
    actions = [
      "dynamodb:DeleteItem",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
    ]
    resources = [aws_dynamodb_table.agent_mcp_sessions.arn]
  }
}

module "agent_mcp" {
  source       = "./modules/lambda_endpoint"
  name         = "${local.prefix}-agent-mcp"
  source_dir   = "${path.root}/../src/agent_mcp"
  route_key    = "ANY /agent/mcp"
  api_id       = aws_apigatewayv2_api.this.id
  api_exec_arn = aws_apigatewayv2_api.this.execution_arn
  timeout      = 60
  memory_size  = 256
  environment = {
    AGENT_RUNTIME_ARN_PARAM = local.agent_ssm_name
    MCP_SESSION_TABLE       = aws_dynamodb_table.agent_mcp_sessions.name
    LOG_LEVEL               = "INFO"
  }
  enable_custom_policy = true
  policy_json          = data.aws_iam_policy_document.agent_mcp.json
}
