# SleepMate AI 🌙

수면 데이터를 저장하고 분석하여, AI가 실제 저장된 데이터 요약을 바탕으로 답변해 주는 개인 수면 비서 서비스입니다.

## 주요 기능

- 100일간의 샘플 수면 데이터 저장
- 날짜, 수면시간, 메모 데이터 추가 및 삭제
- 수면 데이터 수정 API 제공
- 데이터 기간 및 개수 확인
- 평균 / 최대 / 최소 수면시간 분석
- 최근 수면시간 추세 분석
- 저장된 데이터 요약을 반영한 AI 채팅
- AI 응답 중 Loading UI 표시
- 대화 자동 저장
- 이전 대화 목록 조회 및 불러오기
- 대화 삭제

## 기술 스택

### Frontend
- HTML
- CSS
- JavaScript
- Vercel

### Backend
- Python 3.13
- FastAPI
- Uvicorn
- Render

### Database
- Firebase Firestore

### AI
- Codyssey OpenAI-compatible API
- gpt-5-mini

## 서비스 구조

사용자  
↓  
Vercel Frontend  
↓  
Render FastAPI Backend  
↓  
Firebase Firestore + AI API

Firestore에 저장된 수면 데이터를 FastAPI 서버에서 요약하고, 해당 요약 정보를 AI의 System Prompt에 포함하여 사용자의 질문에 데이터 기반으로 답변하도록 구현했습니다.

## 배포 URL

### Frontend
https://sleepmate-ai-sf4j.vercel.app/

### Backend
https://sleepmate-ai.onrender.com/

### Swagger API 문서
https://sleepmate-ai.onrender.com/docs

## 주요 API

### Data
- `POST /api/data` : 수면 데이터 추가
- `GET /api/data` : 수면 데이터 목록 조회
- `PUT /api/data/{id}` : 수면 데이터 수정
- `DELETE /api/data/{id}` : 수면 데이터 삭제
- `GET /api/data/summary` : 수면 데이터 요약

### Conversations
- `POST /api/conversations` : 대화 저장
- `GET /api/conversations` : 대화 목록 조회
- `GET /api/conversations/{id}` : 특정 대화 불러오기
- `DELETE /api/conversations/{id}` : 대화 삭제

### AI Chat
- `POST /api/chat` : 수면 데이터 요약을 기반으로 AI 답변 생성 및 대화 자동 저장

## 데이터 구조

수면 데이터는 다음과 같이 구성됩니다.

- `date` : 날짜
- `value` : 수면시간
- `memo` : 메모

프로젝트 테스트를 위해 100일간의 샘플 수면 데이터를 생성하여 Firestore에 저장했습니다.

## 로컬 실행 방법

### 1. 가상환경 생성

```bash
python -m venv venv
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
CODYSSEY_API_KEY=YOUR_API_KEY
CODYSSEY_BASE_URL=YOUR_API_BASE_URL
CODYSSEY_MODEL=gpt-5-mini
FIREBASE_SERVICE_ACCOUNT_PATH=YOUR_FIREBASE_SERVICE_ACCOUNT_PATH
```

실제 API Key와 Firebase 서비스 계정 인증 파일은 GitHub에 업로드하지 않습니다.

### 4. Backend 실행

```bash
uvicorn main:app --reload
```

### 5. Frontend 실행

```bash
python -m http.server 5500
```

## 보안

- API Key를 환경변수로 관리
- Firebase 서비스 계정 인증정보를 코드에 직접 저장하지 않음
- `.env` 및 Firebase 인증 파일을 `.gitignore`로 제외
- Frontend 코드에 API Key를 노출하지 않음

## 실행 화면

<img width="1366" height="1811" alt="image" src="https://github.com/user-attachments/assets/e5704e5c-ad0b-4524-9cf2-aef8e5a5476e" />
<img width="1506" height="1453" alt="image" src="https://github.com/user-attachments/assets/a08b68be-1172-4b29-a0d1-b3ff55cf951f" />
<img width="1526" height="918" alt="image" src="https://github.com/user-attachments/assets/f9b6c246-46ca-424b-87e7-edf42c9b7eeb" />
