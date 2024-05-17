import asyncio
import sys
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from fastapi.responses import FileResponse
from openai import AsyncOpenAI
import tempfile
import mido
from mido import MidiFile, MidiTrack, Message

import time

from util import get_gpt_notes

print("start")
print("setting model..")
# autochord 패키지가 위치한 src 폴더를 sys.path에 추가합니다.
sys.path.insert(0, '/app/autochord-0.1.4/src')
from autochord import recognize
print("done.")

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ["OPEN_AI_KEY"],
)


app = FastAPI()
router = APIRouter()


@app.get("/")
def read_root():
    return {"Hello": "here is the blms-transceiver."}


@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    try:
        # 업로드된 파일을 메모리에 저장
        input_data = await file.read()
        input_filepath = f"/tmp/{file.filename}"
        lab_filepath = f"/tmp/{file.filename}.lab"

        # 메모리에 저장된 파일을 디스크에 임시로 저장
        with open(input_filepath, "wb") as f:
            f.write(input_data)
        
        # 오디오 파일 처리
        start = time.time()
        notes = recognize(input_filepath, lab_fn=lab_filepath)
        async with client:
            tasks = [get_gpt_notes(notes, "piano", client),
                     get_gpt_notes(notes, "bass", client),
                     get_gpt_notes(notes, "drum", client),
                     ]
            results = await asyncio.gather(*tasks)
        end = time.time()
        new_notes = {}
        for result in results:
            new_notes.update(result)

        mid = MidiFile()
        # 멜로디 트랙 생성
        melody_track = MidiTrack()
        mid.tracks.append(melody_track)
        # 템포 설정 (120 BPM)
        tempo = mido.bpm2tempo(120)
        melody_track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        # 프로그램 체인지 (멜로디: 피아노)
        melody_track.append(Message('program_change', program=0))
        for note in new_notes["piano"]:
            melody_track.append(Message('note_on', note=note[2], velocity=64, time=note[0]))
            melody_track.append(Message('note_off', note=note[2], velocity=64, time=note[1]))

        # 베이스 트랙 생성
        bass_track = MidiTrack()
        # 프로그램 체인지 (베이스: 어쿠스틱 베이스)
        bass_track.append(Message('program_change', program=32))
        mid.tracks.append(bass_track)
        for note in new_notes["bass"]:
            melody_track.append(Message('note_on', note=note[2], velocity=64, time=note[0]))
            melody_track.append(Message('note_off', note=note[2], velocity=64, time=note[1]))

        # 드럼 트랙 생성 (채널 10)
        drum_track = MidiTrack()
        mid.tracks.append(drum_track)

        # 드럼 패턴 작성 (Kick, Snare, Hi-Hat)
        drum_track.append(Message('program_change', program=0, channel=9))

        # 패턴 반복
        for note in new_notes["drum"]:
            drum_track.append(Message('note_on', note=note[2], velocity=64, time=note[0], channel=9))
            drum_track.append(Message('note_off', note=note[2], velocity=64, time=note[1], channel=9))

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mid') as tmp:
            mid.save(tmp.name)
            tmp_path = tmp.name

        # .lab 파일을 메모리에서 반환
        return FileResponse(tmp_path, media_type='audio/midi', filename='other_instruments.mid')
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router, prefix="/api")
