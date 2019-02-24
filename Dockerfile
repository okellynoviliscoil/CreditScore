FROM python:3.7-alpine
MAINTAINER Ofir Kelly (kelly.o@fibi.co.il)

COPY . /CreditScore
WORKDIR /CreditScore
RUN pip install -r requirements.txt
CMD ["python", "app.py"]