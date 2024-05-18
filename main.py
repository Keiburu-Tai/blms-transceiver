import asyncio
import sys
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from fastapi.responses import FileResponse
from openai import AsyncOpenAI
import mido
from mido import MidiFile, MidiTrack, Message
import time
from util import get_gpt_notes

def parse_lab_file(filename):
    chords = []
    with open(filename, 'r') as file:
        for line in file:
            start, end, chord = line.strip().split("\t")
            chords.append(chord)
    return chords

print("start")
print("setting model..")
# autochord 패키지가 위치한 src 폴더를 sys.path에 추가합니다.
sys.path.insert(0, '/app/autochord-0.1.4/src')
from autochord import recognize
print("done.")

client = AsyncOpenAI(
    api_key=os.environ["OPEN_AI_KEY"],
)

app = FastAPI()
router = APIRouter()

@app.get("/")
def read_root():
    return {"Hello": "here is the blms-transceiver."}

@app.post("/init-audio/")
async def process_audio(file: UploadFile = File(...)):
    try:
        # 업로드된 파일을 메모리에 저장
        input_data = await file.read()
        input_filepath = f"/tmp/{file.filename}"
        lab_filepath = f"/tmp/{file.filename}.lab"

        # 메모리에 저장된 파일을 디스크에 임시로 저장
        with open(input_filepath, "wb") as f:
            f.write(input_data)
        print("make .lab")
        
        # 오디오 파일 처리
        start = time.time()
        notes = recognize(input_filepath, lab_fn=lab_filepath)
        filters = parse_lab_file(lab_filepath)

        startTime = time.time()
        piano_note, piano_velocity, base_note = await get_gpt_notes(filters, client, 80)
        endTime = time.time() - startTime
        print(f"Time taken: {endTime} seconds") 

        new_notes = {
            "piano": list(zip(piano_note, piano_velocity)),
            "base": list(zip(base_note, [64] * len(base_note)))  # Assuming constant velocity for the base
        }

        mid = MidiFile()
        
        # 멜로디 트랙 생성
        melody_track = MidiTrack()
        mid.tracks.append(melody_track)
        # 템포 설정 (120 BPM)
        tempo = mido.bpm2tempo(220)
        melody_track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        # 프로그램 체인지 (멜로디: 피아노)
        melody_track.append(Message('program_change', program=0))
        for note, vel in zip(piano_note, piano_velocity):
            if isinstance(note, list):  # 화음인 경우
                for n in note:
                    melody_track.append(Message('note_on', note=n, velocity=vel, time=0))  # 화음 시작
                for n in note:
                    melody_track.append(Message('note_off', note=n, velocity=vel, time=480))  # 화음 종료
            else:  # 단일 노트인 경우
                melody_track.append(Message('note_on', note=note, velocity=vel, time=0))
                melody_track.append(Message('note_off', note=note, velocity=vel, time=480))

        # 베이스 트랙 생성
        bass_track = MidiTrack()
        mid.tracks.append(bass_track)
        bass_track.append(Message('program_change', program=32))
        for note in base_note:
            if isinstance(note, list):  # 화음인 경우
                for n in note:
                    bass_track.append(Message('note_on', note=n, velocity=64, time=0))  # 화음 시작
                for n in note:
                    bass_track.append(Message('note_off', note=n, velocity=64, time=480))  # 화음 종료
            else:  # 단일 노트인 경우
                bass_track.append(Message('note_on', note=note, velocity=64, time=0))
                bass_track.append(Message('note_off', note=note, velocity=64, time=480))

        # 드럼 트랙 생성
        drum_track = MidiTrack()
        mid.tracks.append(drum_track)

        # 드럼 패턴 작성 (Kick, Snare, Hi-Hat)
        drum_track.append(Message('program_change', program=0, channel=9))
        kick = 36    # Bass Drum (C1)
        snare = 38   # Acoustic Snare (D1)
        hihat = 42   # Closed Hi-Hat (F#1)

        # 패턴 반복
        for _ in range(40):
            drum_track.append(Message('note_on', note=kick, velocity=64, time=0, channel=9))
            drum_track.append(Message('note_off', note=kick, velocity=64, time=240, channel=9))

            drum_track.append(Message('note_on', note=hihat, velocity=64, time=0, channel=9))
            drum_track.append(Message('note_off', note=hihat, velocity=64, time=240, channel=9))

            drum_track.append(Message('note_on', note=snare, velocity=64, time=0, channel=9))
            drum_track.append(Message('note_off', note=snare, velocity=64, time=240, channel=9))

            drum_track.append(Message('note_on', note=hihat, velocity=64, time=0, channel=9))
            drum_track.append(Message('note_off', note=hihat, velocity=64, time=240, channel=9))

        # Save the MIDI file in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        midi_file_path = os.path.join(script_dir, "output.mid")
        mid.save(midi_file_path)

        return FileResponse(midi_file_path, filename="output.mid", media_type='application/octet-stream')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        print("make .lab")
        
        # 오디오 파일 처리
        start = time.time()
        notes = recognize(input_filepath, lab_fn=lab_filepath)
        filters = parse_lab_file(lab_filepath)

        startTime = time.time()
        piano_note, piano_velocity, base_note = await get_gpt_notes(filters, client, 40)
        endTime = time.time() - startTime
        print(f"Time taken: {endTime} seconds") 

        new_notes = {
            "piano": list(zip(piano_note, piano_velocity)),
            "base": list(zip(base_note, [64] * len(base_note)))  # Assuming constant velocity for the base
        }

        mid = MidiFile()
        
        # 멜로디 트랙 생성
        melody_track = MidiTrack()
        mid.tracks.append(melody_track)
        # 템포 설정 (120 BPM)
        tempo = mido.bpm2tempo(220)
        melody_track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        # 프로그램 체인지 (멜로디: 피아노)
        melody_track.append(Message('program_change', program=0))
        for note, vel in zip(piano_note, piano_velocity):
            if isinstance(note, list):  # 화음인 경우
                for n in note:
                    melody_track.append(Message('note_on', note=n, velocity=vel, time=0))  # 화음 시작
                for n in note:
                    melody_track.append(Message('note_off', note=n, velocity=vel, time=480))  # 화음 종료
            else:  # 단일 노트인 경우
                melody_track.append(Message('note_on', note=note, velocity=vel, time=0))
                melody_track.append(Message('note_off', note=note, velocity=vel, time=480))

        # 베이스 트랙 생성
        bass_track = MidiTrack()
        mid.tracks.append(bass_track)
        bass_track.append(Message('program_change', program=32))
        for note in base_note:
            if isinstance(note, list):  # 화음인 경우
                for n in note:
                    bass_track.append(Message('note_on', note=n, velocity=64, time=0))  # 화음 시작
                for n in note:
                    bass_track.append(Message('note_off', note=n, velocity=64, time=480))  # 화음 종료
            else:  # 단일 노트인 경우
                bass_track.append(Message('note_on', note=note, velocity=64, time=0))
                bass_track.append(Message('note_off', note=note, velocity=64, time=480))

        # 드럼 트랙 생성
        drum_track = MidiTrack()
        mid.tracks.append(drum_track)

        # 드럼 패턴 작성 (Kick, Snare, Hi-Hat)
        drum_track.append(Message('program_change', program=0, channel=9))
        kick = 36    # Bass Drum (C1)
        snare = 38   # Acoustic Snare (D1)
        hihat = 42   # Closed Hi-Hat (F#1)

        # 패턴 반복
        for _ in range(20):
            drum_track.append(Message('note_on', note=kick, velocity=64, time=0, channel=9))
            drum_track.append(Message('note_off', note=kick, velocity=64, time=240, channel=9))

            drum_track.append(Message('note_on', note=hihat, velocity=64, time=0, channel=9))
            drum_track.append(Message('note_off', note=hihat, velocity=64, time=240, channel=9))

            drum_track.append(Message('note_on', note=snare, velocity=64, time=0, channel=9))
            drum_track.append(Message('note_off', note=snare, velocity=64, time=240, channel=9))

            drum_track.append(Message('note_on', note=hihat, velocity=64, time=0, channel=9))
            drum_track.append(Message('note_off', note=hihat, velocity=64, time=240, channel=9))

        # Save the MIDI file in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        midi_file_path = os.path.join(script_dir, "output.mid")
        mid.save(midi_file_path)

        return FileResponse(midi_file_path, filename="output.mid", media_type='application/octet-stream')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router, prefix="/api")
