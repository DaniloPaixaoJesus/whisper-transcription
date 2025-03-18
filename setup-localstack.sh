#!/bin/bash

# Espera a inicialização do LocalStack
echo "Esperando o LocalStack iniciar..."
#sleep 10

# Cria o tópico SNS
echo "Criando o tópico SNS..."
TOPIC_ARN=$(awslocal sns create-topic --name transcription-topic --query 'TopicArn' --output text)
echo "Tópico SNS criado: $TOPIC_ARN"


# Criar a fila SQS transcription-queue
echo "Criando a fila SQS..."
QUEUE_URL=$(awslocal sqs create-queue --queue-name transcription-queue --query 'QueueUrl' --output text)
echo "Fila SQS criada: $QUEUE_URL"


# Obter o ARN da fila SQS
QUEUE_ARN=$(awslocal sqs get-queue-attributes \
    --queue-url $QUEUE_URL \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' --output text)
echo "ARN da Fila SQS: $QUEUE_ARN"


# Inscrever a fila SQS no tópico SNS
echo "Inscrevendo a fila SQS no tópico SNS..."
awslocal sns subscribe \
    --topic-arn $TOPIC_ARN \
    --protocol sqs \
    --notification-endpoint $QUEUE_ARN
echo "Fila SQS inscrita com sucesso no tópico SNS."


# Permitir que o SNS publique mensagens na fila SQS
echo "Configurando permissões para o SNS enviar mensagens para a SQS..."
awslocal sqs set-queue-attributes \
    --queue-url $QUEUE_URL \
    --attributes '{
      "Policy": "{\"Version\": \"2012-10-17\", \"Statement\": [{\"Effect\": \"Allow\", \"Principal\": \"*\", \"Action\": \"SQS:SendMessage\", \"Resource\": \"'$QUEUE_ARN'\", \"Condition\": {\"ArnEquals\": {\"aws:SourceArn\": \"'$TOPIC_ARN'\"}}}]}"}'
echo "Permissões configuradas."


# Cria o bucket S3
echo "Criando o bucket S3..."
awslocal s3api create-bucket --bucket transcription-bucket

# Configura o CORS no bucket devido ao LocalStack ser localhost
echo "Configurando o CORS no bucket..."
awslocal s3api put-bucket-cors --bucket transcription-bucket --cors-configuration '{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedOrigins": ["*"],
      "ExposeHeaders": ["ETag"]
    }
  ]
}'


echo "Configuração concluída com sucesso."
