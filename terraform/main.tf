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

# Buscar política IAM existente
data "aws_iam_policy" "existing_lambda_policy" {
  name = "lambda_access_policy"
}

resource "aws_iam_role_policy_attachment" "attach_lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = data.aws_iam_policy.existing_lambda_policy.arn
}

# Função Lambda
resource "aws_lambda_function" "video_processor" {
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

  depends_on = [aws_iam_role_policy_attachment.attach_lambda_policy]
}

# Permissão para a Lambda ser acionada por eventos do SQS
resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.video_processor.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = "arn:aws:sqs:us-east-1:980029326297:videos-queue"
}
