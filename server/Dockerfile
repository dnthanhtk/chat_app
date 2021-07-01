FROM python:3.8
WORKDIR /app/backend
COPY requirements.txt /app/backend/
COPY app.py /app/backend/
COPY  . /app/backend/
RUN pip install -r requirements.txt

EXPOSE 9999
CMD ["python", "app.py"]