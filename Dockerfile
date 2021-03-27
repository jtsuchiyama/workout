FROM python:3.7 

ADD requirements.txt / 

RUN pip install -r requirements.txt 

ADD *.py /

ADD templates /templates 

EXPOSE 5000

EXPOSE 8000

CMD gunicorn -b 0.0.0.0:8000  __init__:app 

