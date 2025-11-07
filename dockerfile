FROM python:alpine

ENV LANG C.UTF-8
WORKDIR /app
COPY ./requirements.txt .
COPY ./models/feedback.py ./models/feedback.py
COPY ./models/tiltify.py ./models/tiltify.py
COPY ./utils/utils.py ./utils/utils.py
COPY ./main.py .
COPY ./.env .
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

CMD [ "python3","-OO","main.py" ]