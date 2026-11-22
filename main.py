import os
import json
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

load_dotenv()

app = FastAPI(title="SleepMate AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Firebase 연결
# -------------------------
def init_firebase():
    if not firebase_admin._apps:
        firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        firebase_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

        if firebase_json:
            cred = credentials.Certificate(json.loads(firebase_json))
        elif firebase_path:
            cred = credentials.Certificate(firebase_path)
        else:
            raise RuntimeError("Firebase 인증 정보가 없습니다.")

        firebase_admin.initialize_app(cred)

    return firestore.client()


db = init_firebase()


# -------------------------
# 데이터 형식
# -------------------------
class SleepData(BaseModel):
    date: str
    value: float = Field(gt=0, le=24)
    memo: str = Field(default="", max_length=200)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class ConversationRequest(BaseModel):
    title: str = "새 대화"
    messages: list[dict]


# -------------------------
# 기본 확인
# -------------------------
@app.get("/")
def root():
    return {"message": "SleepMate AI API is running"}


# -------------------------
# 수면 데이터 CRUD
# -------------------------
@app.post("/api/data")
def create_data(item: SleepData):
    doc = db.collection("data").document()

    data = item.model_dump()
    data["created_at"] = datetime.now().isoformat()

    doc.set(data)

    return {"id": doc.id, **data}


@app.get("/api/data")
def get_data():
    docs = db.collection("data").stream()

    result = []

    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        result.append(item)

    result.sort(key=lambda x: x.get("date", ""), reverse=True)

    return result


@app.put("/api/data/{data_id}")
def update_data(data_id: str, item: SleepData):
    ref = db.collection("data").document(data_id)

    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")

    ref.update(item.model_dump())

    return {"id": data_id, **item.model_dump()}


@app.delete("/api/data/{data_id}")
def delete_data(data_id: str):
    ref = db.collection("data").document(data_id)

    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")

    ref.delete()

    return {"message": "삭제되었습니다."}


# -------------------------
# 데이터 요약
# -------------------------
def make_summary():
    docs = db.collection("data").stream()

    data = []

    for doc in docs:
        item = doc.to_dict()

        if "date" in item and "value" in item:
            data.append(item)

    if not data:
        return {
            "count": 0,
            "period": "-",
            "average": 0,
            "max": 0,
            "min": 0,
            "trend": "데이터 없음",
        }

    data.sort(key=lambda x: x["date"])

    values = [float(x["value"]) for x in data]

    average = sum(values) / len(values)

    recent = values[-7:]
    previous = values[-14:-7]

    trend = "비교 데이터 부족"

    if previous:
        recent_avg = sum(recent) / len(recent)
        previous_avg = sum(previous) / len(previous)

        difference = recent_avg - previous_avg

        if difference > 0.2:
            trend = "최근 수면시간이 증가하는 추세"
        elif difference < -0.2:
            trend = "최근 수면시간이 감소하는 추세"
        else:
            trend = "최근 수면시간이 비슷하게 유지되는 추세"

    return {
        "count": len(data),
        "period": f'{data[0]["date"]} ~ {data[-1]["date"]}',
        "average": round(average, 2),
        "max": max(values),
        "min": min(values),
        "trend": trend,
    }


@app.get("/api/data/summary")
def get_summary():
    return make_summary()


# -------------------------
# 대화 저장/조회/삭제
# -------------------------
@app.post("/api/conversations")
def create_conversation(conversation: ConversationRequest):
    doc = db.collection("conversations").document()

    data = {
        "title": conversation.title,
        "messages": conversation.messages,
        "created_at": datetime.now().isoformat(),
    }

    doc.set(data)

    return {"id": doc.id, **data}


@app.get("/api/conversations")
def get_conversations():
    docs = db.collection("conversations").stream()

    result = []

    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        result.append(item)

    result.sort(
        key=lambda x: x.get("created_at", ""),
        reverse=True,
    )

    return result


@app.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    doc = db.collection("conversations").document(conversation_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")

    return {"id": doc.id, **doc.to_dict()}


@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(conversation_id: str):
    ref = db.collection("conversations").document(conversation_id)

    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")

    ref.delete()

    return {"message": "대화가 삭제되었습니다."}


# -------------------------
# AI 채팅
# -------------------------
@app.post("/api/chat")
def chat(request: ChatRequest):
    api_key = os.getenv("CODYSSEY_API_KEY")
    base_url = os.getenv("CODYSSEY_BASE_URL")
    model = os.getenv("CODYSSEY_MODEL")

    if not api_key or not base_url:
        raise HTTPException(
            status_code=500,
            detail="AI API 설정이 없습니다.",
        )

    if not model:
        raise HTTPException(
            status_code=500,
            detail="CODYSSEY_MODEL 설정이 없습니다.",
        )

    summary = make_summary()

    system_prompt = f"""
너는 사용자의 수면 데이터를 분석해 주는 SleepMate AI 비서다.

현재 저장된 수면 데이터 요약:
- 기간: {summary['period']}
- 데이터 개수: {summary['count']}개
- 평균 수면시간: {summary['average']}시간
- 최대 수면시간: {summary['max']}시간
- 최소 수면시간: {summary['min']}시간
- 최근 추세: {summary['trend']}

반드시 위 데이터를 바탕으로 답변한다.
의학적 진단을 하지 말고 간결하고 이해하기 쉽게 답변한다.
"""

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message},
            ],
        )

        answer = response.choices[0].message.content

        conversation = {
            "title": request.message[:30],
            "messages": [
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": answer},
            ],
            "created_at": datetime.now().isoformat(),
        }

        db.collection("conversations").add(conversation)

        return {
            "answer": answer,
            "summary": summary,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI 응답 생성 중 오류가 발생했습니다: {str(e)}",
        )