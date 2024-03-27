import json
import os
import random
import re

MY_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(MY_PATH, "data")

# 엑셀에서 CSV로 변환된 파일이 필요합니다.
# csv 를 딕셔너리로 변경하는 코드를 제거하고, json 파일을 첨부했습니다
with open(os.path.join(DATA_DIR, "rulebased_data.json"), "r", encoding="utf-8") as json_file:
    data_dict = json.load(json_file)


def generate_rule_based_questions(position: str, jd: str, cv: str):

    keywords_questions = data_dict
    keywords_list = data_dict

    ai = ["ai", "머신러닝", "딥러닝", "ml", "dl"]
    fe = ["프론트엔드", "frontend"]
    be = ["백엔드", "backend"]

    question_essential = []
    if position == "AI":
        ai_list = keywords_questions[str(ai)]
        ai_list = random.sample(ai_list, 2)
        question_essential.extend(ai_list)
    if position == "FE":
        fe_list = keywords_questions[str(fe)]
        fe_list = random.sample(fe_list, 2)
        question_essential.extend(fe_list)
    if position == "BE":
        be_list = keywords_questions[str(be)]
        be_list = random.sample(be_list, 2)
        question_essential.extend(be_list)

    def generate_question_essential(position, d):
        question_essential = []

        if position == "AI":
            ai_list = d[str(ai)]
            ai_list = random.sample(ai_list, 2)
            question_essential.extend(ai_list)

        if position == "FE":
            fe_list = d[str(fe)]
            fe_list = random.sample(fe_list, 2)
            question_essential.extend(fe_list)

        if position == "BE":
            be_list = d[str(be)]
            be_list = random.sample(be_list, 2)
            question_essential.extend(be_list)

        return question_essential

    question_essential = generate_question_essential(position, keywords_questions)

    github = ["github", "git", "깃허브", "깃헙", "깃"]
    cs = ["cs 지식", "cs지식", "자료구조", "알고리즘"]
    docker = ["docker", "가상 환경", "가상환경"]

    for keyword in github:
        pattern = " " + keyword
        if re.findall(pattern, jd):
            question_essential.extend(random.sample(keywords_questions[str(github)], 1))
            break
    for keyword in cs:
        pattern = " " + keyword
        if re.findall(pattern, jd):
            question_essential.extend(random.sample(keywords_questions[str(cs)], 1))
            break
    for keyword in docker:
        pattern = " " + keyword
        if re.findall(pattern, jd):
            question_essential.extend(random.sample(keywords_questions[str(docker)], 1))
            break

    dl_framework = ["딥러닝 프레임워크", "deep learning framework", " tensorflow", "pytorch", "keras"]
    if position == "AI":
        for keyword in dl_framework:
            if re.findall("^[a-z]" + keyword + "^[a-z]", jd):
                question_essential.extend(random.sample(keywords_questions[str(dl_framework)], 1))

    java = ["자바", "java"]
    python = ["파이썬", "python"]
    cpp = ["c++"]
    javascript = ["javascript", "자바스크립트"]
    go = ["go"]

    # 채용공고에 언어가 몇 개 포함되어 있는지 확인
    langlist_jd = []
    langlist_cv = []
    langtype = [java, python, cpp, javascript, go]

    for keywords in langtype:
        for keyword in keywords:
            pattern1 = " " + keyword + " "
            pattern2 = " " + keyword + ","
            if pattern1 in cv or pattern2 in jd:
                langlist_jd.append(keywords)
                break

    for keywords in langtype:
        for keyword in keywords:
            pattern1 = " " + keyword + " "
            pattern2 = " " + keyword + ","
            if pattern1 in cv or pattern2 in cv:
                langlist_cv.append(keywords)
                break

    langlist = []

    if langlist_cv and not langlist_jd:
        question_essential.extend(random.sample(keywords_questions[str(langlist_cv[0])], 1))

    if len(langlist_jd) == 1:
        lang = random.sample(keywords_questions[str(langlist_jd[0])], 1)
        question_essential.extend(lang)

    if len(langlist_jd) > 2:
        for keyword in langlist_jd:
            if keyword in langlist_cv:
                langlist.append(keyword)

        if langlist:
            lang = random.sample(keywords_questions[str(langlist[0])], 1)
        else:
            lang = random.sample(keywords_questions[str(langlist_jd[0])], 1)

    print(*question_essential, sep="\n")

    question_by_jd = []

    # Remove specific elements from the list keywords_list
    keywords_list = [
        i
        for i in keywords_list
        if i not in [github, cs, docker, dl_framework, java, python, go, cpp, javascript, ai, be, fe]
    ]

    for keywords in keywords_list:
        for keyword in keywords:
            if keyword in jd:
                question_by_jd.extend(keywords_questions[str(keywords)])

    if question_by_jd:
        question_by_jd = random.sample(question_by_jd, 10 - len(question_essential))
        questions = question_essential + question_by_jd

    questions = question_essential + question_by_jd
    questions = questions[:6]

    return questions


if __name__ == "__main__":
    # 직군 선택이 필요합니다.
    position = "AI"
    position = "BE"
    position = "FE"

    position = "BE"
    # jd와 cv text 파일이 필요합니다.
    jd = open("jd.txt", "r", encoding="utf-8").read().lower()  # 채용 공고 input
    cv = open("cv.txt", "r", encoding="utf-8").read().lower()  # 이력서/자소서 input

    print(*generate_rule_based_questions(position="BE", jd=jd, cv=cv), sep="\n")