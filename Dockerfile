FROM python

RUN apt-get update
RUN apt-get install pari-gp -y
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
COPY src /app
COPY 9.txt /app
COPY defconfig.json /app
#RUN python /app/db.py

CMD ["python","/app/cirno.py"]