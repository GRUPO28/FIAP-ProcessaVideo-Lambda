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

# Buscar função Lambda existente
data "aws_lambda_function" "existing_lambda" {
  function_name = "video_processor"
}

# Buscar fila SQS existente
data "aws_sqs_queue" "existing_video_queue" {
  name = "videos-queue"
}

# Permissão para a Lambda ser acionada por eventos do SQS
resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.existing_lambda.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = data.aws_sqs_queue.existing_video_queue.arn
}

# Configurar a integração da SQS com a Lambda
resource "aws_lambda_event_source_mapping" "sqs_lambda_trigger" {
  event_source_arn = data.aws_sqs_queue.existing_video_queue.arn
  function_name    = data.aws_lambda_function.existing_lambda.arn
  batch_size       = 10
}