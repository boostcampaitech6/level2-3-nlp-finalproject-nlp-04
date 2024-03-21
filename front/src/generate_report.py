import openai
import os
import re
from langchain.chains import SequentialChain,LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain import PromptTemplate
import plotly.graph_objs as go
from PIL import Image
import matplotlib.pyplot as plt
import plotly.io as pio
import base64
import ast
import json

def generate_llm_sub_chain(llm, template: str, output_key: str):
    # 프롬프트 템플릿 정의
    prompt_template = PromptTemplate.from_template(template)
    # 프롬프트와 출력 키를 사용하여 LLM 체인 생성
    sub_chain = LLMChain(llm=llm, prompt=prompt_template, output_key=output_key)
    return sub_chain

def load_conversation(path):
    """
    대화 기록을 로드하는 함수입니다.

    :param path: 대화 기록 파일의 경로
    :type path: str

    :return: 대화 기록을 분리한 리스트
    :rtype: list
    """
    split_prefix = "\n\n$$$$$$$$$$\n\n"
    with open(path, 'r', encoding='utf-8') as f:
        all_conversation_history_txt = f.read()
    all_conversation_history_lst = all_conversation_history_txt.split(split_prefix)
    return all_conversation_history_lst

def generate_report(llm_conversation,
                    llm_total,
                    all_conversation_history_lst,
                    job_nm,main_job_ability,
                    question_prompt,
                    total_prompt):
    """
    면접 리포트를 생성하는 함수입니다.

    :param llm_conversation: 대화를 생성하기 위한 언어 모델
    :type llm_conversation: LLM (Language Model) 객체

    :param llm_total: 전체 리포트를 생성하기 위한 언어 모델
    :type llm_total: LLM (Language Model) 객체

    :param all_conversation_history_lst: 면접 대화 기록을 담고 있는 리스트
    :type all_conversation_history_lst: list

    :param job_nm: 직무명
    :type job_nm: str

    :param main_job_ability: 주요 직무 역량
    :type main_job_ability: str

    :param question_prompt: 대화문 생성을 위한 프롬프트 템플릿
    :type question_prompt: str

    :param total_prompt: 전체 리포트 생성을 위한 프롬프트 템플릿
    :type total_prompt: str

    :return: 면접 리포트 및 콜백 결과
    :rtype: tuple
    """
    total_chains_lst = []
    # 1. 대질문 별 피드백 결과 Chain 생성
    for i, question_answer_result in enumerate(all_conversation_history_lst):
        # temp 프롬프트 지정
        temp_prompt = question_prompt.replace("{question_answer_result}",str(question_answer_result))
        # chain 생성: input= Question-Answer 대화문  /  output= 대화문 별 생성 요건
        chain = generate_llm_sub_chain(llm_conversation, temp_prompt, f"conversation_report_{i}")
        # 생성된 chain을 Total list에 append
        total_chains_lst.append(chain)

    # 2. 전체 리포트 피드백 코드 생성
    # chain 생성: input= Question-Answer 대화문 X 6  /  output= 전반적인 피드백 리포트
    chain = generate_llm_sub_chain(llm_total, total_prompt, f"total_report")
    total_chains_lst.append(chain)
        
    # 3. overall_chain생성
    input_var_nm = ["job_nm", "main_job_ability"]
    input_variables = [job_nm, main_job_ability]
    input_variables_dic = dict(zip(input_var_nm, input_variables))
    output_variables = [f"conversation_report_{i}" for i in range(len(total_chains_lst)-1)] + ["total_report"]

    overall_report_chain = SequentialChain(
        chains=total_chains_lst,
        input_variables=input_var_nm,
        output_variables=output_variables,
        verbose=True,
        return_all=True
    )
    with get_openai_callback() as callback:
        result = overall_report_chain(input_variables_dic)
    return result, callback
    
def clean_text(inputString):
    """
    텍스트 데이터를 정제하는 함수입니다.

    :param inputString: 정제할 텍스트 데이터
    :type inputString: str

    :return: 특수 문자와 공백을 제거한 정제된 텍스트 데이터
    :rtype: str
    """
    text_rmv = re.sub('[-=+,#/\?:^.@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]', ' ', inputString)
    text_rmv = ' '.join(text_rmv.split())
    return text_rmv

def clean_kpi_item(inputDict):
    """
    KPI 항목을 정제하는 함수입니다.

    :param inputDict: KPI 항목을 포함한 딕셔너리
    :type inputDict: dict

    :return: 정제된 KPI 항목을 담은 딕셔너리
    :rtype: dict
    """
    cleanDict = {}
    try:
        if len(inputDict['핵심 역량']) < 2:
            cleanDict['핵심 역량'] = "핵심 역량을 불러올 수 없습니다."
        elif len(inputDict['긍정적인 측면']) < 2:
            cleanDict['긍정적인 측면'] = "긍정적인 측면을 불러올 수 없습니다"
        elif len(inputDict['개선해야할 측면']) < 2:
            cleanDict['개선해야할 측면'] = "개선해야할 측면을 불러올 수 없습니다"
        elif inputDict['점수'] == '':
            cleanDict['점수'] ='0'
        else:
            cleanDict = inputDict
        print(f"DEBUG | clean_kpi_item 점수 : {cleanDict['점수']} , type : {type(cleanDict['점수'])}")
        return cleanDict
    except:
        return {'핵심 역량' : '핵심 역량을 불러올 수 없습니다.',
                '긍정적인 측면' : '긍정적인 측면을 불러올 수 없습니다',
                '개선해야할 측면' : '개선해야할 측면을 불러올 수 없습니다',
                '점수' : '0'}
    
def final_report_parsing(total_report):
    """
    전체 리포트에서 전반적인 피드백을 추출하는 함수입니다.

    :param total_report: 전체 리포트
    :type total_report: str

    :return: 추출된 전반적인 피드백 문자열
    :rtype: str
    """
    try:
        fianl_report = ast.literal_eval(total_report)['전반적인 피드백']
        return fianl_report
    except:
        if "전반적인 피드백" in total_report:
            fianl_report = total_report.split("전반적인 피드백")[1]
            return clean_text(fianl_report)
        else:
            return "피드백 결과를 불러올 수 없습니다."
        
def conversation_output_parsing(report):
    """
    대화 리포트에서 각 대화 세그먼트를 추출하는 함수입니다.

    :param report: 대화 리포트를 담고 있는 딕셔너리
    :type report: dict

    :return: 각 대화 세그먼트를 담은 리스트
    :rtype: list
    """
    count = 0
    text_list = []
    for k in report.keys():
        if "conversation_report" in k:
            count += 1
    # print(count)
    for conversation_id in range(count):
        text_list.append(report[f"conversation_report_{conversation_id}"])
    return text_list

def kpi_report_parsing(total_report):
    """
    전체 리포트에서 역량별 피드백을 추출하여 정제하는 함수입니다.

    :param total_report: 전체 리포트
    :type total_report: str

    :return: 추출 및 정제된 역량별 피드백 리스트
    :rtype: list
    """
    clean_kpi_report = []
    try:
        kpi_report = ast.literal_eval(total_report)['역량별 피드백']
        for item in kpi_report:
            clean_kpi_report.append(clean_kpi_item(item))
        return clean_kpi_report
    except Exception as ex:
        print(f"ERROR | kpi_report_parsing | ",ex)

def kpi_output_parsing(report):
    """
    전체 리포트에서 KPI 피드백과 전반적인 피드백을 추출하는 함수입니다.

    :param report: 전체 리포트를 담고 있는 딕셔너리
    :type report: dict

    :return: KPI 피드백 및 전반적인 피드백을 담은 튜플
    :rtype: tuple
    """
    kpi_report = kpi_report_parsing(report['total_report'])
    fianl_report = final_report_parsing(report['total_report'])
    return kpi_report,fianl_report

def kpi_radar_chart(kpi_report):
    """
    KPI 리포트를 바탕으로 레이더 차트를 생성하는 함수입니다.

    :param kpi_report: KPI 리포트를 담고 있는 리스트
    :type kpi_report: list of dict

    :return: 레이더 차트 이미지를 Base64로 인코딩한 문자열
    :rtype: str
    """
    plt.rc('font', family='Nanumsquare') # For MacOS

    data = [
        go.Scatterpolar(
            r=[int(kpi_report[0]['점수']),
               int(kpi_report[1]['점수']), 
               int(kpi_report[2]['점수']), 
               int(kpi_report[3]['점수']), 
               int(kpi_report[4]['점수']),
               int(kpi_report[5]['점수']), 
               int(kpi_report[0]['점수'])],
            theta=[kpi_report[0]['핵심 역량'], 
                   kpi_report[1]['핵심 역량'],
                   kpi_report[2]['핵심 역량'], 
                   kpi_report[3]['핵심 역량'], 
                   kpi_report[4]['핵심 역량'], 
                   kpi_report[5]['핵심 역량'], 
                   kpi_report[0]['핵심 역량']],
            text=[str(int(kpi_report[0]['점수'])),
                  str(int(kpi_report[1]['점수'])), 
                  str(int(kpi_report[2]['점수'])),
                  str(int(kpi_report[3]['점수'])), 
                  str(int(kpi_report[4]['점수'])), 
                  str(int(kpi_report[5]['점수']))],
            fill="toself",
            line_color="#2D5AF0",
            mode='lines+markers+text',
            name="Data",
            
        )
    ]
    layout = go.Layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100],showticklabels=True)),
                        paper_bgcolor='white',plot_bgcolor='#2D5AF0',width=400, height=300)

    fig = go.Figure(data=data, layout=layout)
    fig.update_polars(angularaxis_type="category") # chaining-friendly
    fig.update_traces(textposition='top center', textfont_size=12)
    # Convert figure to an image buffer
    image_bytes = pio.to_image(fig, format='png')

    # Encode the image buffer to base64
    image_str = base64.b64encode(image_bytes).decode()
    return image_str

def save_report(path,data):
    with open(path,"w",encoding='utf-8') as f:
        json.dump(data,f)