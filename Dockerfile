FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY ./src /app/
RUN chmod +x /app/wait-for-it.sh
CMD ["python", "my_app.py"]

