# Video Processor Lambda Hackaton FIAP

Este projeto processa vídeos e cria um arquivo ZIP contendo os quadros extraídos.

## Estrutura
- **app/controllers/**: Contém a função Lambda principal
- **app/core/**: Contém a lógica de processamento de vídeo e criação de ZIP
- **tests/**: Testes unitários

### Dependências e estrutura para o teste local

1. **Configuração inicial:**
   - Certifique-se de ter todas as dependências instaladas com:
     ```
     pip install -r requirements.txt
     ```

2. **Executar os testes:**
   - Rode os testes com:
     ```
     python -m unittest discover tests/
     ```

3. **Resultados esperados:**
   - O teste verificará se o ZIP foi criado corretamente a partir dos frames simulados e se os arquivos esperados estão dentro dele.

