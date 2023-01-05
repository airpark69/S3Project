FROM python:3.8-slim-buster



# Korean Fonts
RUN apt-get update
RUN apt install -y fontconfig
RUN mkdir -p /usr/share/fonts/nanumfont
RUN apt install -y wget
RUN apt install -y unzip  
RUN wget http://cdn.naver.com/naver/NanumFont/fontfiles/NanumFont_TTF_ALL.zip
RUN unzip NanumFont_TTF_ALL.zip -d /usr/share/fonts/nanumfont
RUN fc-cache -f && rm -rf /var/cache/*

# jdk 설치
#   JDK
RUN apt-get update && apt-get install -y openjdk-11-jre

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/jre
ENV PATH=$PATH:$JAVA_HOME/bin

# bash install
RUN apt install bash

# Language
ENV LANG=ko_KR.UTF-8 \
    LANGUAGE=ko_KR.UTF-8

# Set the timezone in docker
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

RUN apt-get install -y tzdata

# Docker Demon Port Mapping
ENV PORT 80
EXPOSE $PORT

WORKDIR /usr/src
RUN apt-get -y update
RUN apt install -y curl

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt -y install ./google-chrome-stable_current_amd64.deb
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/` curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN mkdir chrome
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/src/chrome
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY run.py ./
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]