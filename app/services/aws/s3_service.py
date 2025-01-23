import boto3


class S3Service:
    def __init__(self):
        self.s3 = boto3.client('s3')

    def get_object_stream(self, bucket_name, s3_key):
        try:
            response = self.s3.get_object(Bucket=bucket_name, Key=s3_key)
            return response['Body']
        except Exception as e:
            print(f"Erro ao baixar objeto: {e}")
            raise

    def upload_buffer_to_s3(self, buffer, bucket_name, s3_key):
        try:
            self.s3.upload_fileobj(buffer, bucket_name, s3_key)
            print(f"Arquivo importado no s3://{bucket_name}/{s3_key}")
        except Exception as e:
            print(f"Erro ao realizar upload no S3: {e}")
            raise

    def list_objects_in_bucket(self, bucket_name, prefix=None):
        try:
            if prefix:
                response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            else:
                response = self.s3.list_objects_v2(Bucket=bucket_name)

            objects = response.get('Contents', [])
            return [obj['Key'] for obj in objects]
        except Exception as e:
            print(f"Error listar objetos do bucket: {bucket_name}: {e}")
            raise