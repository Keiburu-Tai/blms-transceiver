from ast import literal_eval
from openai import AsyncOpenAI
import json

async def get_gpt_notes(notes: list, client: AsyncOpenAI, time: int):
    # Define the content as a single string with the notes included
    content = '''목적: 이 LLM은 주어진 특정 코드 진행을 기반으로 피아노와 베이스 노트 및 세기 정보를 처리하여, piano_note, piano_velocity, base_note, base_velocity 리스트로 반환합니다. 이 리스트들은 "Spain", "Take The A Train", "Come Rain Or Come Shine", "Taking A Chance On Love", "On Green Dolphin Street"와 같은 재즈 노래들의 느낌을 살려 생성됩니다.
    입력 형식:

    특정 코드 진행 (예: [Cmaj7, G7, Am7, Dm7, G7, Cmaj7])
    최대 음의 값: 127
    최대 음의 세기: 100
    리스트 길이: 30
    출력 형식 (json):

    piano_note: 피아노의 음의 값 리스트
    piano_velocity: 피아노의 음의 세기 리스트
    base_note: 베이스의 음의 값 리스트
    base_velocity: 베이스의 음의 세기 리스트
    요구사항:

    피아노와 베이스가 각각의 개성을 살리면서 서로를 받쳐주는 구성
    솔로 파트와 반주 파트가 포함된 구성
    화음과 솔로를 강조한 출력
    음의 값은 127을 넘지 않음
    음의 세기가 100을 넘지 않음
    리스트 길이는 30으로 제한
    특정 코드 진행을 기반으로 리스트를 생성
    결과는 "Spain", "Take The A Train", "Come Rain Or Come Shine", "Taking A Chance On Love", "On Green Dolphin Street"와 같은 재즈 곡의 느낌을 살릴 것
    예시 입력
    [Cmaj7, G7, Am7, Dm7, G7, Cmaj7]

    예시 출력
    LLM은 다음과 같은 형식으로 출력을 반환해야 합니다:

    piano_note = [60, 64, 67, 71, 60, 67, 71, 72, 74, 55, 59, 62, 67, 71, 55, 62, 67, 69, 72, 53, 57, 60, 64, 67, 53, 60, 64, 66, 69]
    piano_velocity = [90, 85, 87, 88, 92, 95, 87, 89, 93, 88, 85, 87, 88, 92, 90, 85, 87, 88, 92, 88, 85, 87, 88, 92, 90, 85, 87, 88, 92]
    base_note = [36, 40, 43, 45, 36, 43, 45, 47, 48, 31, 35, 38, 43, 47, 31, 38, 43, 45, 47, 29, 33, 36, 40, 43, 29, 36, 40, 42, 45]
    base_velocity = [80, 78, 79, 77, 82, 85, 87, 89, 91, 72, 75, 78, 83, 87, 70, 78, 83, 85, 87, 68, 73, 75, 78, 82, 66, 73, 78, 80, 83]
    수행 방법
    주어진 특정 코드 진행을 기반으로 풍부한 화음과 각 악기의 솔로를 추가하여 피아노와 베이스의 음의 값 및 세기를 리스트 길이 40에 맞춰 조정합니다.
    음의 값이 127을 넘지 않도록 합니다.
    음의 세기가 100을 넘지 않도록 합니다.
    피아노와 베이스가 서로의 솔로를 받쳐주도록 구성합니다.
    특정 코드 진행을 기반으로 리스트를 생성합니다. 예시 코드 진행: [Cmaj7, G7, Am7, Dm7, G7, Cmaj7]
    피아노와 베이스는 각각 "Spain", "Take The A Train", "Come Rain Or Come Shine", "Taking A Chance On Love", "On Green Dolphin Street"와 같은 재즈 곡의 느낌을 살려 생성합니다.
    화음과 솔로를 강조하여 출력합니다.
    예시 화음 표현
    각 음의 값과 세기를 바탕으로 화음을 구성합니다. 예시에서는 C Major 7, G7, Am7, Dm7 화음을 사용했습니다.

    C Major 7: [60, 64, 67, 71]
    G7: [67, 71, 74, 77]
    Am7: [69, 72, 76, 79]
    Dm7: [62, 65, 69, 72]
    이와 같은 화음들은 재즈 곡에서 자주 사용되며, 이를 바탕으로 다양한 음의 값과 세기를 조합하여 리스트를 생성합니다.

    반드시 예시 출력 형태로만 답하세요.
    '''
    # Concatenate the content with the notes
    content += f"\n입력된 코드 진행: {str(notes)}"

    completion = await client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": content
            },
            {
                "role": "user",
                "content":f" 출력예시의 리스트의 길이는 {str(time)}이어야합니다. {str(notes)}"
            }
        ]
    )
    
    content = completion.choices[0].message.content

    parsed_content = json.loads(content)
    
    # 각 리스트를 추출
    piano_note = parsed_content['piano_note']
    piano_velocity = parsed_content['piano_velocity']
    base_note = parsed_content['base_note']
    base_velocity = parsed_content['base_velocity']

    # 추출된 리스트들을 출력
    print("Piano Notes:", piano_note)
    print("Piano Velocity:", piano_velocity)
    print("Base Notes:", base_note)
    print("Base Velocity:", base_velocity)
    
    return piano_note, piano_velocity, base_note
