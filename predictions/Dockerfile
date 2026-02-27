FROM public.ecr.aws/lambda/python:3.13-arm64

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py model.py config.py api_client.py ./

CMD ["handler.handler"]
