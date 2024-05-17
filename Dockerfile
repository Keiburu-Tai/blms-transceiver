FROM tensorflow/tensorflow:2.13.0

WORKDIR /app

COPY . /app
# RUN pip install autochord
RUN pip install scipy gdown librosa vamp lazycats fastapi uvicorn openai mido

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]