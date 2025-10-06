FROM python:3.14.0

WORKDIR /app/backend/

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["python",".app/py"]