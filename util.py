from ast import literal_eval
from openai import AsyncOpenAI


async def get_gpt_notes(notes: list, instrument: str, client: AsyncOpenAI) -> dict:

    completion = await client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": "너는 autochord 라이브러리를 통해서 기타 연주를 녹음한 wav 파일의 chord를 분석한 리스트를 받고, 여기에 어울리는 "
                        f"{instrument}의 MIDI note number list를 사용자가 아래에 적은 형식으로 JSON 결과만 출력해. \n"
                        "Input gives out a list of tuples in the format based on second: \n"
                        "(chord start(sec), chord end(sec), guitar chord name)\n"
                        "Input example: \n"
                        "[(0.0, 5.944308390022676, 'D:maj'),"
                        "(5.944308390022676, 7.476825396825397, 'C:maj'), "
                        "(7.476825396825397, 18.250884353741498, 'D:maj'),"
                        "(18.250884353741498, 19.736961451247165, 'C:maj'), "
                        "(19.736961451247165, 23.3, 'E')] \n"
                        "Output should take out a list of tuples in the format not json nor dict base on mili second "
                        "time: \n"
                        f"(chord start(int), chord end(int), {instrument} MIDI note number(int))\n"
                        "Output example:"
                        "{'response': [(0, 2000, 52),"
                        "(2000, 4000, 45),"
                        "(4000, 10000, 32),"
                        "(10000, 17000, 12),"
                        "(17000, 23000, 28)]}"
             },
            {"role": "user", "content": str(notes)}
        ]
    )

    return {instrument: literal_eval(completion.choices[0].message.content)["response"]}
