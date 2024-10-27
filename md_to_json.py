import json
import re
import copy

# 정규 표현식 패턴 정의
question_block_pattern = r"(##\s\d+\..+?)(?=##|\Z)"  # 문제 블록 추출
title_pattern = r"\.\s(.+?)\s*---"                   # 문제 제목 추출
option_pattern = r"- \[( |x)\]\s(.+)"                # 문항과 선택지 추출
image_pattern = r"!\[.*?\]\((.+?)\)"                 # 이미지 파일 경로 추출
explanation_pattern = r"> \*\*Explanation:\*\*\s*(.+)"  # 설명 추출

# 문제 블록 추출 함수
def extract_question_blocks(content: str):
    return re.finditer(question_block_pattern, content, re.DOTALL)

# 각 문제 블록 내 요소들 추출 함수
def extract_question_elements(question_block: str):
    # 문제 제목 추출
    title_match = re.search(title_pattern, question_block)
    title = title_match.group(1).strip() if title_match else ""

    # 각각의 요소를 위한 복사본 생성
    block_copy_for_image = copy.deepcopy(question_block)
    block_copy_for_explanation = copy.deepcopy(question_block)
    block_copy_for_options = copy.deepcopy(question_block)

    # 이미지 경로 추출
    image_match = re.search(image_pattern, block_copy_for_image)
    image_path = image_match.group(1) if image_match else None

    # 설명 추출
    explanation_match = re.search(explanation_pattern, block_copy_for_explanation)
    explanation = explanation_match.group(1).strip() if explanation_match else ""

    # 선택지 및 정답 추출
    options = []
    correct_answer = []
    for option_match in re.finditer(option_pattern, block_copy_for_options):
        option_text = option_match.group(2).strip()
        options.append(option_text)
        if option_match.group(1) == 'x':  # 정답 여부 확인
            correct_answer.append(option_text)

    return title, options, correct_answer, image_path, explanation

# 파일 읽기 및 JSON 저장
def create_questions_json(file_path: str, output_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    questions_data = []
    for idx, block_match in enumerate(extract_question_blocks(content), start=1):
        question_block = block_match.group(0).strip()
        
        # 요소 추출
        title, options, correct_answer, image_path, explanation = extract_question_elements(question_block)

        # 문제 데이터 구성
        question_data = {
            "index": idx,
            "title": title,
            "image": image_path,
            "options": options,
            "answer": correct_answer if len(correct_answer) > 1 else correct_answer[0] if correct_answer else "",
            "explanation": explanation
        }
        questions_data.append(question_data)

    # JSON 파일로 저장
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(questions_data, json_file, indent=2, ensure_ascii=False)
    print(f"JSON 데이터가 '{output_path}' 파일에 저장되었습니다.")

# 함수 실행
create_questions_json("3~5.md", "questions.json")
