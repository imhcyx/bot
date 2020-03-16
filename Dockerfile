FROM python

RUN mkdir /app
WORKDIR /app
COPY src /app
COPY requirements.txt /app
RUN pip install -r /code/requirements.txt

CMD ["python","/app/src/main.py"]