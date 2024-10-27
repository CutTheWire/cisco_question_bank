import json
import os
import random
from typing import List

import uvicorn
from docx import Document
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# CORS 설정 (모든 출처 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 디렉토리 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# JSON 파일 로드
with open("questions.json", "r", encoding="utf-8") as file:
    questions_data = json.load(file)

# 요청 바디 모델 정의
class AnswerRequest(BaseModel):
    answer: List[str]

# 모든 문제를 제공하는 API 엔드포인트
@app.get("/get-questions")
async def get_questions():
    # 모든 문제를 반환하되, 순서를 랜덤하게 섞어서 반환
    randomized_questions = random.sample(questions_data, len(questions_data))
    questions_for_frontend = [
        {
            "index": question["index"],
            "title": question["title"],
            "options": question["options"],
            "image": question.get("image")
        }
        for question in randomized_questions
    ]
    return questions_for_frontend

# 사용자가 제출한 답변을 확인하는 API 엔드포인트
@app.post("/check-answer/{question_index}")
async def check_answer(question_index: int, request: AnswerRequest):
    question = next((q for q in questions_data if q["index"] == question_index), None)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    # 정답이 여러 개인 경우 처리
    correct_answer = question["answer"]
    correct = sorted(request.answer) == sorted(correct_answer)
    explanation = question.get("explanation", "")
    return {
        "correct": correct,
        "correct_answer": correct_answer,
        "explanation": explanation
    }

# 보고서 생성 및 Word 파일 반환 API
@app.post("/download-report")
async def download_report(request: Request):
    data = await request.json()
    correct_count = data.get("correctCount", 0)
    incorrect_list = data.get("incorrectList", [])

    # Word 문서 생성
    doc = Document()
    doc.add_heading("퀴즈 결과 보고서", level=1)
    doc.add_paragraph(f"맞은 개수: {correct_count}")
    doc.add_paragraph(f"틀린 개수: {len(incorrect_list)}")

    doc.add_heading("틀린 문제 목록:", level=2)
    for item in incorrect_list:
        doc.add_paragraph(f"문제: {item['title']}")
        doc.add_paragraph(f"정답: {item['correct_answer']}")
        doc.add_paragraph("")

    # Word 파일로 저장
    output_path = "report.docx"
    doc.save(output_path)

    # Word 파일 응답으로 반환
    return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="report.docx")

# 루트 경로에서 index.html 반환
@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8111)
