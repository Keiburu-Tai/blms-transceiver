FROM tensorflow/tensorflow:2.13.0

WORKDIR /app
COPY . /app
# RUN pip install autochord
RUN pip install scipy gdown librosa vamp lazycats
ENTRYPOINT ["python3", "auto-chord.py"]