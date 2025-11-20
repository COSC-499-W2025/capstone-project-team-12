FROM python:3.13.9-slim-trixie

WORKDIR /app

# Install git (required for pydriller/GitPython)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

#upgrade pip to latest version
RUN pip install -U pip
#install all requirements
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY --exclude=backend/configs/ ./ ./
#download used ML models and preproc dictionaries.
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader punkt punkt_tab stopwords wordnet averaged_perceptron_tagger averaged_perceptron_tagger_eng
ENV PYTHONPATH="${PYTHONPATH}:/app/backend/"
EXPOSE 80

CMD ["python","-u","./init.py"]