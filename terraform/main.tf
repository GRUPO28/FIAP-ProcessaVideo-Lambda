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



