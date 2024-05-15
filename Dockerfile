FROM python:3.11
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY main.py /app/main.py
CMD chainlit run main.py -w --host 0.0.0.0 --port 8000
