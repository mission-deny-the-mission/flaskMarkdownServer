#syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt -y update
RUN apt -y install pandoc
RUN apt -y install texlive-full
RUN pip3 install gunicorn
RUN mkdir workspace
COPY app.py .
COPY password_hashing.py .
EXPOSE 80
CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app:app" ]
