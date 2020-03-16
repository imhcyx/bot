FROM python

RUN mkdir /app
WORKDIR /app
COPY src /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt

CMD ["python","/app/main.py"]