FROM python:3.13.9-trixie

WORKDIR /app

COPY ./ ./

RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm
# added this to get preprocess_text() to work properly
RUN python -m nltk.downloader punkt punkt_tab stopwords wordnet averaged_perceptron_tagger averaged_perceptron_tagger_eng

EXPOSE 80

CMD ["python","./app.py"]