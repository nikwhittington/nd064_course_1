FROM python:2.7
LABEL maintainer="Nik Whittington"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python init_db.py
EXPOSE 3111/tcp
# command to run on container start
CMD [ "python", "app.py" ]