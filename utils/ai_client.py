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


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("
"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("
    return json.loads(text.strip())


def summarize_and_quiz(text: str, num_questions: int = 5) -> dict:
    prompt = (
        "Դու աշակերտների համար նախատեսված ուսուցչական օգնական ես։\n"
        "Հետևյալ տեքստից կազմիր՝\n"
        "1. summary: կարճ սեղմագիր հայերենով, միայն կարևոր փաստեր, ամսաթվեր և բանաձևեր, markdown bullet-ներով։\n"
        f"2. questions: ճիշտ {num_questions} բազմակի ընտրության հարց հայերենով։\n"
        "Յուրաքանչյուր հարց պետք է ունենա՝ question (string), options (4 տարբերակ), "
        "answer_index (ճիշտ տարբերակի ինդեքսը 0-3), explanation (կարճ բացատրություն)։\n\n"
        "Պատասխանիր ՄԻԱՅՆ վավեր JSON-ով, առանց լրացուցիչ տեքստի։\n\n"
        "ՏԵՔՍՏ:\n"
        f"{text}"
    )
    response = _model().generate_content(
        prompt,
        generation_config={"temperature": 0.3, "response_mime_type": "application/json"},
    )
    return _parse_json(response.text)


def evaluate_spoken_answer(topic: str, transcript: str) -> str:
    prompt = (
        "Դու բարյացակամ, բայց խիստ ռեպետիտոր ես։\n"
        f"Թեմա՝ {topic}\n\n"
        "Աշակերտը բանավոր պատմեց հետևյալը՝\n"
        f"{transcript}\n\n"
        "Տուր հետադարձ կապ հայերենով՝\n"
        "1. Ինչ է ճիշտ և ինչ լավ է պատմած\n"
        "2. Ինչ է բաց թողել կամ սխալ է նշել (կոնկրետ)\n"
        "3. Խորհուրդ՝ ինչ պետք է կրկնել\n"
        "Եղիր կարճ և օգտակար։"
    )
    response = _model().generate_content(prompt, generation_config={"temperature": 0.4})
    return response.text


def transcribe_audio(audio_bytes: bytes) -> str:
    raise RuntimeError(
        "Ձայնի ճանաչումը այս տարբերակում հասանելի չէ։ Օգտագործիր տեքստային մուտքը։"
    )


def generate_study_plan(subject: str, exam_date: str, days_left: int, topics: str) -> str:
    prompt = (
        "Դու ուսումնական պլանավորման մասնագետ ես։\n"
        f"Առարկա՝ {subject}\n"
        f"Քննության օր՝ {exam_date} (մնացել է {days_left} օր)\n"
        f"Թեմաներ՝ {topics}\n\n"
        "Կազմիր օր առ օր գրաֆիկ հայերենով։ Յուրաքանչյուր օրվա համար՝ "
        "ինչ թեմաներ սովորել, կրկնության առաջադրանք, ժամանակի մոտավոր բաշխում։ "
        "Վերջում՝ քննության օրվա խորհուրդ։"
    )
    response = _model().generate_content(prompt, generation_config={"temperature": 0.5})
    return response.text
