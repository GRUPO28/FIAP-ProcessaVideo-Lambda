provider "aws" {
  region = "us-east-1"
}

# Gerar um identificador único para o nome da role
resource "random_id" "role_suffix" {
  byte_length = 4
}

# Role da Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role_${random_id.role_suffix.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Permissões adicionais para a Lambda acessar a SQS
resource "aws_iam_policy" "lambda_sqs_policy" {
  name        = "lambda_sqs_policy_${random_id.role_suffix.hex}"
  description = "Permissões para a Lambda acessar SQS"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        Resource = data.aws_sqs_queue.existing_video_queue.arn
      }
    ]
  })
}

# Anexar política de permissões da SQS à role da Lambda
resource "aws_iam_role_policy_attachment" "attach_lambda_sqs_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_sqs_policy.arn
}

# Buscar política IAM existente
data "aws_iam_policy" "existing_lambda_policy" {
  name = "lambda_access_policy"
}

resource "aws_iam_role_policy_attachment" "attach_lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = data.aws_iam_policy.existing_lambda_policy.arn
}

# Buscar a Lambda existente, se ela já existir
data "aws_lambda_function" "existing_lambda" {
  function_name = "video_processor"
}

# Criar Lambda apenas se não existir
resource "aws_lambda_function" "video_processor" {
  count         = try(length(data.aws_lambda_function.existing_lambda.arn), 0) > 0 ? 0 : 1
  function_name = "video_processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.8"
  timeout       = 60
  memory_size   = 512
  s3_bucket     = "processa-video-infra"
  s3_key        = "video_processor.zip"

  environment {
    variables = {
      TABLE_NAME = "Videos"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.attach_lambda_policy, aws_iam_role_policy_attachment.attach_lambda_sqs_policy]
}

# Buscar fila SQS existente
data "aws_sqs_queue" "existing_video_queue" {
  name = "videos-queue"
}

# Permissão para a Lambda ser acionada por eventos do SQS
resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = coalesce(
    try(data.aws_lambda_function.existing_lambda.function_name, ""),
    try(length(aws_lambda_function.video_processor) > 0 ? aws_lambda_function.video_processor[0].function_name : "")
  )
  principal     = "sqs.amazonaws.com"
  source_arn    = data.aws_sqs_queue.existing_video_queue.arn
}

# Configurar a integração da SQS com a Lambda
resource "aws_lambda_event_source_mapping" "sqs_lambda_trigger" {
  event_source_arn = data.aws_sqs_queue.existing_video_queue.arn
  function_name    = coalesce(
    try(data.aws_lambda_function.existing_lambda.arn, ""),
    try(length(aws_lambda_function.video_processor) > 0 ? aws_lambda_function.video_processor[0].arn : "")
  )
  batch_size       = 10
}

# Output corrigido para lidar com "count"
output "lambda_arn" {
  value = coalesce(
    try(data.aws_lambda_function.existing_lambda.arn, ""),
    try(length(aws_lambda_function.video_processor) > 0 ? aws_lambda_function.video_processor[0].arn : "")
  )
}
