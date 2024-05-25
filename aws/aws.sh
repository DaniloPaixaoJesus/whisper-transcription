

aws sqs create-queue --queue-name transcription-queue

aws sns create-topic --name transcription-topic
QUEUE_ARN=$(aws sqs get-queue-attributes --queue-url https://sqs.us-east-1.amazonaws.com/381491951305/transcription-queue --attribute-names QueueArn --query "Attributes.QueueArn" --output text)
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:381491951305:transcription-topic --protocol sqs --notification-endpoint $QUEUE_ARN


aws s3api create-bucket --bucket app-transcription-bucket

aws s3api put-bucket-cors --bucket transcription-bucket --cors-configuration '{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedOrigins": ["*"],
      "ExposeHeaders": ["ETag"]
    }
  ]
}'

aws iam create-role --role-name app-transcription-lambda-role --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'


aws iam attach-role-policy --role-name app-transcription-lambda-role --policy-arn arn:aws:iam::381491951305:policy/texttranscription_policy



zip -r lambda_function.zip lambda_function.py

aws lambda create-function --function-name receiveVideoFile --zip-file fileb:////home/ec2-user/py-projects/whisper-transcription/lambda/lambda_function.zip --handler lambda_function.lambda_handler --runtime python3.8 --role arn:aws:iam::381491951305:role/app-transcription-lambda-role

aws lambda wait function-active-v2 --function-name receiveVideoFile

aws lambda add-permission --function-name receiveVideoFile --principal s3.amazonaws.com --statement-id some-unique-id --action "lambda:InvokeFunction" --source-arn arn:aws:s3:::app-transcription-bucket --source-account 000000000000

aws s3api put-bucket-notification-configuration --bucket app-transcription-bucket --notification-configuration file:////home/ec2-user/py-projects/whisper-transcription/localstack/notification.json
