import boto3


class DynamoDBService:
    STATUS_MAPPING = {
        "Aguardando": 0,
        "Processando": 1,
        "Pronto": 2,
        "Falhou": 3
    }

    def __init__(self, table_name="Video"):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def get_item(self, key_value):
        try:
            key = {"Id": key_value}
            response = self.table.get_item(Key=key)
            return response.get("Item")
        except Exception as e:
            error_message = (
                f"Erro ao obter item da tabela {self.table.name}: "
                f"Um erro ocorreu ({e.response['Error']['Code']}) durante a operação {e.operation_name}: {e.response['Error']['Message']}"
            ) if hasattr(e, 'response') else str(e)
            print(error_message)
            return None

    def put_item(self, item):
        try:
            self.table.put_item(Item=item)
            print("Item salvo com sucesso.")
        except Exception as e:
            error_message = (
                f"Erro ao inserir item: "
                f"Um erro ocorreu ({e.response['Error']['Code']}) durante a operação {e.operation_name}: {e.response['Error']['Message']}"
            ) if hasattr(e, 'response') else str(e)
            print(error_message)
            raise

    def update_status(self, key_value, new_status):
        try:
            key = {"Id": key_value}
            update_expression = "SET #status = :status"
            expression_values = {":status": new_status}
            expression_names = {"#status": "Status"}

            self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ExpressionAttributeNames=expression_names,
                ConditionExpression="attribute_exists(Id)"
            )
            print(f"Status do item {key_value} atualizado para {new_status}.")
        except Exception as e:
            print(f"Erro ao atualizar o status do item com ID {key_value}: {e}")
            raise

    def update_item(self, key_value, update_expression, expression_values):
        try:
            key = {"Id": key_value}

            self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            print("Item atualizado com sucesso.")
        except Exception as e:
            error_message = (
                f"Erro ao atualizar item: "
                f"Um erro ocorreu ({e.response['Error']['Code']}) durante a operação {e.operation_name}: {e.response['Error']['Message']}"
            ) if hasattr(e, 'response') else str(e)
            print(error_message)
            raise

    def delete_item(self, key_value):
        try:
            key = {"Id": key_value}
            self.table.delete_item(Key=key)
            print("Item excluído com sucesso.")
        except Exception as e:
            error_message = (
                f"Erro ao excluir item: "
                f"Um erro ocorreu ({e.response['Error']['Code']}) durante a operação {e.operation_name}: {e.response['Error']['Message']}"
            ) if hasattr(e, 'response') else str(e)
            print(error_message)
            raise
