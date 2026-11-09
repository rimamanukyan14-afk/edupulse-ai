import json
import os

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

_configured = False


def _model(model_name: str = "gemini-1.5-flash"):
    global _configured
    if not _configured:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is missing in the Secrets settings.")
        genai.configure(api_key=api_key)
        _configured = True
    return genai.GenerativeModel(model_name)


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("
", 1)[0]
    return text.strip()


def summarize_and_quiz(text: str, num_questions: int = 5) -> dict:
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

Պատասխանիր ՄԻԱՅՆ վավեր JSON-ով, առանց լրացուցիչ տեքստի կամ json ֆենսերի։

ՏԵՔՍՏ:
"""
{text}
"""
"""
    response = _model().generate_content(
        prompt,
        generation_config={"temperature": 0.3, "response_mime_type": "application/json"},
    )
    return json.loads(_strip_fences(response.text))


def evaluate_spoken_answer(topic: str, transcript: str) -> str:
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
    response = _model().generate_content(prompt, generation_config={"temperature": 0.4})
    return response.text


def transcribe_audio(audio_bytes: bytes) -> str:
    raise RuntimeError(
        "Ձայնի ճանաչումը այս տարբերակում հասանելի չէ։ Օգտագործիր տեքստային մուտքը։"
    )


def generate_study_plan(subject: str, exam_date: str, days_left: int, topics: str) -> str:
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
    response = _model().generate_content(prompt, generation_config={"temperature": 0.5})
    return response.text
   
