import sys
import os
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from fastapi.responses import StreamingResponse

import time

print("start")
print("setting model..")
# autochord 패키지가 위치한 src 폴더를 sys.path에 추가합니다.
sys.path.insert(0, '/app/autochord-0.1.4/src')
from autochord import recognize
print("done.")
app = FastAPI()

router = APIRouter()

@app.get("/")
def read_root():
    return {"Hello": "here is the blms-transceiver"}

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
        recognize(input_filepath, lab_fn=lab_filepath)
        end = time.time()
        
        print(f"Processing time: {end - start:.5f} sec")
        
        # .lab 파일을 메모리로 읽어오기
        with open(lab_filepath, "rb") as lab_file:
            lab_data = lab_file.read()

        # 디스크에 임시 저장된 파일들 삭제
        os.remove(input_filepath)
        os.remove(lab_filepath)

        # .lab 파일을 메모리에서 반환
        return StreamingResponse(BytesIO(lab_data), media_type='application/octet-stream', headers={'Content-Disposition': f'attachment; filename="{file.filename}.lab"'})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router, prefix="/api")