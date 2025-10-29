FROM python:3.13.9-trixie

WORKDIR /app

COPY ./ ./

RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

EXPOSE 80

CMD ["python","./app.py"]