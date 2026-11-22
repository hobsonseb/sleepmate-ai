from datetime import date, timedelta
import random

from main import db

random.seed(42)

collection = db.collection("data")

# 중복 방지를 위해 기존 수면 데이터 삭제
for doc in collection.stream():
    doc.reference.delete()

# 최근 100일 수면 데이터 생성
today = date.today()

for i in range(100):
    sleep_date = today - timedelta(days=99 - i)

    # 5.5 ~ 8.5시간 사이의 샘플 수면시간
    sleep_hours = round(random.uniform(5.5, 8.5), 1)

    if sleep_hours >= 7.5:
        memo = "푹 잠"
    elif sleep_hours < 6.5:
        memo = "늦게 잠듦"
    else:
        memo = "보통"

    collection.add({
        "date": sleep_date.isoformat(),
        "value": sleep_hours,
        "memo": memo,
    })

print("수면 데이터 100개 저장 완료!")