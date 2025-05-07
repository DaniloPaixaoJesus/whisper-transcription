# Whisper Transcription

Whisper Transcription é uma aplicação para transcrição de vídeos, permitindo upload de arquivos ou fornecimento de URLs para processamento. O resultado é enviado por e-mail e armazenado em um bucket S3.

## 📌 Requisitos

- **Docker** e **Docker Compose**
- **AWS CLI** instalado
- **LocalStack** configurado corretamente
- **Python 3.9+**

## 🔧 Configuração

Crie a rede externa no Docker para compartilhar recursos do LocalStack entre diferentes projetos:

```sh
docker network create localstack-network
```

Antes de iniciar o LocalStack, configure as credenciais de teste:

```sh
aws configure set aws_access_key_id test
aws configure set aws_secret_access_key test
aws configure set region us-east-1
```

Garanta que o **arquivo `setup-localstack.sh` tenha permissão de execução**:

```sh
chmod +x setup-localstack.sh
```

## 🚀 Executando o Projeto

Para rodar o ambiente utilizando Docker Compose:

```sh
docker-compose up --build
```

## 🛠️ Funcionalidades

- Transcrição de áudio de vídeos utilizando Whisper AI.
- Resumo das transcrições via OpenAI GPT-4.
- Upload de arquivos de vídeo ou fornecimento de URLs.
- Envio dos resultados por e-mail.
- Integração com AWS S3 e SQS via LocalStack.

## 📂 Estrutura do Projeto

```
whisper-transcription/
│── src/
│   ├── aws/                    # Integração com AWS (S3, SQS)
│   ├── config/                 # Configuração do projeto
│   ├── controllers/            # Controladores de API
│   ├── models/                 # Modelos de requisição e resposta
│   ├── services/               # Lógica de transcrição
│   ├── utils/                  # Utilitários (download, email, etc.)
│   ├── main_sqs_consumer.py    # Consumidor da fila SQS
│   ├── main_uvicorn.py         # Servidor FastAPI
│── setup-localstack.sh         # Script de inicialização do LocalStack
│── docker-compose.yml          # Configuração dos serviços Docker
│── Dockerfile                  # Configuração do container da aplicação
│── requirements.txt            # Dependências do projeto
│── README.md                   # Documentação do projeto
```

## 📝 Testando Funcionalidades via AWS CLI

### 📌 Upload de um arquivo para o S3

```sh
aws --endpoint-url=http://localhost:4566 s3 cp exemplo.m4a s3://transcription-bucket/video-download-from-front-end/
```

### 📌 Listar objetos no bucket

```sh
aws --endpoint-url=http://localhost:4566 s3api list-objects --bucket transcription-bucket --output json
```

### 📌 Publicar uma mensagem no tópico SNS

```sh
aws --endpoint-url=http://localhost:4566 sns publish     --topic-arn arn:aws:sns:us-east-1:000000000000:transcription-topic     --message '{
        "bucket-name": "transcription-bucket",
        "bucket-key": "video-download-from-front-end/exemplo.mp4",
        "file-name": "exemplo.m4a",
        "size": 12345,
        "event-time": "2025-03-18T12:00:00Z",
        "transaction-id": "123e4567-e89b-12d3-a456-426614174000"
    }'     --subject "Novo Arquivo Recebido"
```

### 📌 Purgar mensagens da fila SQS

```sh
aws --endpoint-url=http://localhost:4566 sqs purge-queue     --queue-url http://localhost:4566/000000000000/transcription-queue
```

### 📌 Enviar mensagem para a fila SQS manualmente

```sh
aws --endpoint-url=http://localhost:4566 sqs send-message     --queue-url http://localhost:4566/000000000000/transcription-queue     --message-body '{ "file-name": "test.mp4", "bucket-name": "transcription-bucket", "bucket-key": "video-download-from-front-end/exemplo.mp4", "transaction-id": "123e4567-e89b-12d3-a456-426614174000" }'
```
