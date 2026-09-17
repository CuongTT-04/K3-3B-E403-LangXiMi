#!/usr/bin/env python3
"""
Mining Evidence Script - Track D2 (Học từ lỗi trước)
Author: Trần Đình Hinh (Data & Eval Lead) - Nhóm LangXiMi (C4 - E403)

Mục đích:
- Khai phá dữ liệu từ tutor_turns.csv (data/vlearn-pack/chatlog/tutor_turns.csv)
- Chứng minh chuẩn B (Evidence): Số liệu đếm được + Trích dẫn nguyên văn + Tái lập được
"""

import os
import csv
import sys

def find_data_file():
    candidates = [
        "../K4-3B-Day05-06-AI-Product-Hackathon/data/vlearn-pack/chatlog/tutor_turns.csv",
        "/home/hinhpython/K4-3B-Day05-06-AI-Product-Hackathon/data/vlearn-pack/chatlog/tutor_turns.csv",
        "data/vlearn-pack/chatlog/tutor_turns.csv"
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def analyze_tutor_turns(csv_path):
    print(f"=== BẮT ĐẦU MINING DỮ LIỆU TỪ: {csv_path} ===")
    total_turns = 0
    empty_understanding_level = 0
    probing_question_count = 0
    quiz_queries = []

    quiz_keywords = ["quizz", "quiz", "trắc nghiệm", "bài tập ôn", "tạo câu hỏi", "luyện tập"]

    with open(csv_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_turns += 1
            
            # Check understanding_level
            lvl = row.get("understanding_level", "").strip()
            if not lvl or lvl.lower() in ["none", "null", ""]:
                empty_understanding_level += 1

            # Check pedagogical action
            pedagogy = row.get("move_used", "").strip().lower()
            if "ask_probing_question" in pedagogy:
                probing_question_count += 1

            # Check student query asking for quiz / practice
            user_msg = row.get("student_question", "").lower()
            turn_id = row.get("turn_id", f"Turn_{total_turns}")
            if any(k in user_msg for k in quiz_keywords):
                quiz_queries.append({
                    "turn_id": turn_id,
                    "student_message": row.get("student_question", ""),
                    "tutor_response": row.get("tutor_reply", "")[:120] + "..."
                })

    print(f"\n1. TỔNG SỐ LƯỢT TƯƠNG TÁC: {total_turns:,}")
    pct_empty = (empty_understanding_level / total_turns) * 100 if total_turns else 0
    print(f"2. Trường 'understanding_level' bị bỏ trống: {empty_understanding_level:,} / {total_turns:,} ({pct_empty:.2f}%)")
    
    pct_probe = (probing_question_count / total_turns) * 100 if total_turns else 0
    print(f"3. Nước đi sư phạm 'ask_probing_question': {probing_question_count:,} / {total_turns:,} ({pct_probe:.2f}%)")
    
    print(f"\n4. NHU CẦU LÀM QUIZ / ÔN TẬP CỦA HỌC VIÊN: {len(quiz_queries)} lượt")
    print("--- Trích dẫn tiêu biểu (Evidence Chuẩn B) ---")
    for item in quiz_queries[:5]:
        print(f"- Mã turn [{item['turn_id']}]:")
        print(f"  + Học viên: \"{item['student_message']}\"")
        print(f"  + Phản hồi của Tutor: \"{item['tutor_response']}\"\n")

if __name__ == "__main__":
    path = find_data_file()
    if not path:
        print("Không tìm thấy file tutor_turns.csv trong các đường dẫn mẫu. Vui lòng kiểm tra lại.")
        sys.exit(1)
    analyze_tutor_turns(path)
