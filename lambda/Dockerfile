FROM public.ecr.aws/lambda/python:3.8

RUN mkdir /lambda
WORKDIR /lambda

#RUN mkdir /lambda-entrypoint.sh
#WORKDIR /lambda-entrypoint.sh

COPY /lambda/lambda_function.py . 
COPY /lambda/requirements.txt .

RUN pip install -r requirements.txt


CMD ["lambda_function.lambda_handler"]
