import os
import json
import random
import re

# JSON 파일을 로드하여 데이터를 가져옵니다.
FILE_NAME = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "rulebased_data.json")  # 필요한 값에 접근하기 위해 경로 설정
with open(FILE_NAME, "r", encoding="utf-8") as json_file: 
    data_dict = json.load(json_file)

def list_extend_questions_based_on_keywords(data_dict, jd, position):
    # 키워드로 딕셔너리 검색을 위한 keywords

    # 분야
    ai = ['ai', '머신러닝', '딥러닝', 'ml', 'dl']
    fe = ['프론트엔드', 'frontend']
    be = ['백엔드', 'backend']

    # 공통
    github = ['github', 'git', '깃허브', '깃헙', '깃']
    cs = ['cs 지식', 'cs지식', '자료구조', '알고리즘']
    docker = ['docker', '가상 환경', '가상환경']

    # 언어
    java = ['자바', 'java']
    python = ['파이썬', 'python']
    cpp = ['c++']
    javascript = ['javascript', '자바스크립트']
    go = ['go']

    keyword_groups = [github, cs, ai, fe, be, cpp, docker, java, python, javascript, go]
    
    # 반환값이 저장될 리스트
    question_essential = []

    # user 에서 선정된 position 을 기준으로 질문 2개 선정
    if position == 'AI':
        ai_list = data_dict[str(ai)]
        ai_list = random.sample(ai_list, 3)
        question_essential.extend(ai_list)
    
    if position == 'FE':
        fe_list = data_dict[str(fe)]
        fe_list = random.sample(fe_list, 3)
        question_essential.extend(fe_list)
    
    if position == 'BE':
        be_list = data_dict[str(be)]
        be_list = random.sample(be_list, 3)
        question_essential.extend(be_list)
    
    

    for keys in keyword_groups:
        # jd 기반 키워드 매칭으로, 매칭된 키워드 마다 2개씩 랜덤하게 질문을 선정합니다
        # JD에서 keywords 리스트의 항목을 검사하여 일치하는 첫 번째 항목을 data_key로 사용합니다.
     
        data_key = next((keyword for keyword in keys if re.search(r'\b' + re.escape(keyword) + r'\b', jd, re.IGNORECASE)), None)
        if data_key:
            # data_dict에서 data_key에 해당하는 질문 목록을 가져옵니다.
            questions = data_dict.get(data_key, [])
            
            # question_essential에 없는 질문만 필터링합니다.
            new_questions = [q for q in questions if q not in question_essential]
            
            # 새로운 질문 목록에서 랜덤하게 2개를 선택하여 추가합니다.
            if new_questions:
                question_essential.extend(random.sample(new_questions, 2))
    
    # 3개만 랜덤하게 선정합니다.
    question_essential = random.sample(question_essential, k=3)
    
    return question_essential

if __name__ == "__main__":
    jd = "자바스크립트를 사용하여 프론트엔드 개발을 하고 싶습니다."
    print(*list_extend_questions_based_on_keywords(data_dict, jd, position="FE"), sep="\n")