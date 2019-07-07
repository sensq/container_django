FROM python:3-alpine

RUN mkdir /codes
WORKDIR /codes
COPY requirements.txt /codes

RUN pip install -r requirements.txt

COPY apiserver.py /codes

CMD ["python3","/codes/apiserver.py"]