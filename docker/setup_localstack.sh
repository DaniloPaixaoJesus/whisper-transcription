#!/bin/bash

awslocal s3 mb s3://full-transcriptions
awslocal s3 mb s3://summary-transcriptions
awslocal s3 mb s3://video-uploads
awslocal sqs create-queue --queue-name transcription-queue
