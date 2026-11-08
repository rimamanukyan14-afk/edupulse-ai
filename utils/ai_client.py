import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY-ը բացակայում է .env ֆայլում։")
        _client = OpenAI(api_key=api_key)
    return _client


def summarize_and_quiz(text: str, num_questions: int = 5) -> dict:
    """Վերադարձնում է {'summary': str, 'questions': [...]}"""
    prompt = f"""
Դու աշակերտների համար նախատեսված ուսուցչական օգնական ես։
Հետևյալ տեքստից կազմիր՝
1. "summary" — կարճ սեղմագիր հայերենով՝ միայն կարևոր փաստեր, ամսաթվեր և բանաձևեր (markdown bullet-ներով)։
2. "questions" — ճիշտ {num_questions} բազմակի ընտրության հարց հայերենով։
   Յուրաքանչյուր հարց պետք է ունենա՝
   - "question": string
   - "options": 4 տարբերակ (array of strings)
   - "answer_index": ճիշտ տարբերակի ինդեքսը (0-3)
   - "explanation": կարճ բացատրություն

Պատասխանիր ՄԻԱՅՆ վավեր JSON-ով, առանց լրացուցիչ տեքստի կամ `json ֆենսերի։

ՏԵՔՍՏ:
\"\"\"
{text}
\"\"\"
"""
    response = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    return json.loads(response.choices[0].message.content)


def evaluate_spoken_answer(topic: str, transcript: str) -> str:
    """Վերլուծում է ձայնագրված պատասխանը և տալիս հետադարձ կապ։"""
    prompt = f"""
Դու բարյացակամ, բայց խիստ ռեպետիտոր ես։
Թեմա՝ {topic}

Աշակերտը բանավոր պատմեց հետևյալը՝
\"\"\"{transcript}\"\"\"

Տուր հետադարձ կապ հայերենով՝
1. ✅ Ինչ է ճիշտ և ինչ լավ է պատմած
2. ❌ Ինչ է բաց թողել կամ սխալ է նշել (կոնկրետ)
3. 💡 Խորհուրդ՝ ինչ պետք է կրկնել
Եղիր կարճ և օգտակար։
"""
    response = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content


def transcribe_audio(audio_bytes: bytes) -> str:
    """Ձայնը տեքստի է վերածում Whisper-ով (հայերեն)։"""
    import io

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "recording.wav"
    result = get_client().audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="hy",
    )
    return result.text


def generate_study_plan(subject: str, exam_date: str, days_left: int, topics: str) -> str:
    """Կազմում է օրական անհատական քննական ճանապարհային քարտեզ։"""
    prompt = f"""
Դու ուսումնական պլանավորման մասնագետ ես։
Առարկա՝ {subject}
Քննության օր՝ {exam_date} (մնացել է {days_left} օր)
Թեմաներ՝ {topics}

Կազմիր օր առ օր գրաֆիկ հայերենով։ Յուրաքանչյուր օրվա համար՝
- Օր N (ամսաթիվ) — ինչ թեմաներ սովորել
- Կրկնության առաջադրանք
- Ժամանակի մոտավոր բաշխում
Վերջում՝ քննության օրվա խորհուրդ։
"""
    response = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content
