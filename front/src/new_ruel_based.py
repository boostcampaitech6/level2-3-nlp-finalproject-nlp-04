import json
import random
import re

# JSON 파일을 로드하여 데이터를 가져옵니다.
with open('/root/feat_maxseats/level2-3-nlp-finalproject-nlp-04/temp/룰베이스드/simplified_data.json', 'r', encoding='utf-8') as json_file:
    data_dict = json.load(json_file)

   
def list_extend_questions_based_on_keywords(data_dict,jd,position):
    # 키워드로 딕셔너리 검색을 위한 keywords
    ai = "['ai', '머신러닝', '딥러닝', 'ml', 'dl']"
    fe = ['프론트엔드', 'frontend']
    be = ['백엔드', 'backend']

    github = ['github', 'git', '깃허브', '깃헙', '깃']
    cs = ['cs 지식', 'cs지식', '자료구조', '알고리즘']
    docker = ['docker', '가상 환경', '가상환경']


    java = ['자바', 'java']
    python = ['파이썬', 'python']
    cpp = ['c++']
    javascript = ['javascript', '자바스크립트']
    go = ['go']

    keyword_groups = [github, cs, ai, fe, be, cpp, docker,java,python,javascript,go]
    
    # 반환값이 저장될 리스트
    question_essential = []

    # user 에서 선정된 position 을 기준으로 질문 2개 선정
    if position == 'AI':
        ai_list = data_dict['ai']
        ai_list = random.sample(ai_list, 2)
        question_essential.extend(ai_list)
    
    if position == 'FE':
        fe_list = data_dict[str(fe)]
        fe_list = random.sample(fe_list, 2)
        question_essential.extend(fe_list)
    
    if position == 'BE':
        be_list = data_dict[str(be)]
        be_list = random.sample(be_list, 2)
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
    
    len_question = len(question_essential)
    # 만약 룰베이스드로 선정된 질문이 10개 이하인경우, 부족한 수 만큼 cs 질문으로 채워줍니다
    if len_question < 10 :
        l = 10 - len_question

        cs_list = data_dict['cs지식']

        cs_list = random.sample(cs_list, l)   
        
        # question_essential에 없는 질문만 필터링하고 l개 랜덤 선택
        filtered_cs_list = [q for q in cs_list if q not in question_essential]
        selected_questions = random.sample(filtered_cs_list, min(l, len(filtered_cs_list)))
        
        question_essential.extend(selected_questions)
    
    return question_essential


# print(list_extend_questions_based_on_keywords(data_dict,jd,position="AI"))