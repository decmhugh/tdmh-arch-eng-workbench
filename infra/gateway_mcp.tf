data "aws_iam_policy_document" "gateway_mcp" {
  statement {
    actions   = ["bedrock-agentcore:InvokeGateway"]
    resources = [aws_bedrockagentcore_gateway.agent.gateway_arn]
  }
}

module "gateway_mcp" {
  source        = "./modules/lambda_endpoint"
  name          = "${local.prefix}-gateway-mcp"
  source_dir    = "${path.root}/../src/gateway_mcp"
  route_key     = "ANY /gateway/mcp"
  api_id        = aws_apigatewayv2_api.this.id
  api_exec_arn  = aws_apigatewayv2_api.this.execution_arn
  authorizer_id = aws_apigatewayv2_authorizer.mcp_bearer.id
  timeout       = 28
  memory_size   = 128
  environment = {
    GATEWAY_MCP_URL = aws_bedrockagentcore_gateway.agent.gateway_url
    LOG_LEVEL       = "INFO"
  }
  enable_custom_policy = true
  policy_json          = data.aws_iam_policy_document.gateway_mcp.json
}
