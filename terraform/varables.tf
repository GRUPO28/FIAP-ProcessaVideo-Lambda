variable "region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "lambda_bucket" {
  description = "S3 bucket para armazenar o código da Lambda"
  default     = "processa-video-infra"
}
