FROM python:3.9
WORKDIR /app
COPY . /app

RUN pip install pillow

CMD ["python3", "locate_obstacles.py", "sample_input/map.txt", "2.5", "1.5"]