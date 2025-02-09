output "lambda_arn" {
  description = "ARN da Lambda criada"
  value       = aws_lambda_function.video_processor.arn
}
