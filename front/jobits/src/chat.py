import openai
import time

def make_initial_args(main_question,user_name):
    """
    초기 상태 및 인자를 설정하는 함수입니다.

    :param main_question: 주요 질문과 대응되는 딕셔너리
    :type main_question: dict
    :param user_name: 사용자의 이름
    :type user_name: str

    :return: 초기 인자들로 구성된 리스트
    :rtype: list
    """
    # Initialize Sub Question args
    initial_questions = list(main_question)

    # 전체 대질문의 개수. 6이 될 예정
    whole_counts = len(initial_questions)

    # argument값 생성, session state에 초기값이 없을 경우애만 값 세팅
    initial_args_lst = [{"all_conversation_history":[]}
                        , {"conversation_history":[]} # Conversation history update
                        , {"max_conversation_count":3} # MAX 꼬리 질문 횟수
                        , {"conversation_count":0} # 현재 질문 count, 질문이 끝날때마다 +1 & 꼬리질문 끝날때 마다 초기화
                        , {"total_question_count":0} # 전체 질문 수 count, 질문이 끝날때마다 +1 됨
                        , {"initial_questions_idx":0} # 대질문 할당 index, 대질문이 끝날때마다 하나씩 +1 됨
                        , {"messages":[{
                            "role":"assistant" # Initialize chat history, 첫 Message 시작은 인사로 시작
                            ,"content": f"'{user_name}' 면접자님. 환영합니다. 지금부터 AI 면접을 시작하도록 하겠습니다.\n\n 아래 질문에 대해 답변해주세요."
                                    }]
                        }
                        ]
    return initial_questions,whole_counts,initial_args_lst

def ggori_chat_with_gpt3(message
                        , conversation_history
                        , conversation_count
                        , max_conversation_count
                        ):
    """
    사용자와 GPT-3 모델 사이의 대화를 처리하는 함수입니다.

    :param message: 사용자의 입력 메시지
    :type message: str
    :param conversation_history: 대화 기록을 담고 있는 리스트
    :type conversation_history: list
    :param conversation_count: 현재 질문 카운트
    :type conversation_count: int
    :param max_conversation_count: 최대 꼬리 질문 횟수
    :type max_conversation_count: int

    :return: GPT-3 모델의 답변과 업데이트된 대화 기록
    :rtype: tuple
    """
    if conversation_count <= max_conversation_count:
        conversation_history.append({"role": "user", "content": message}) # 입력한 User의 message 입력

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history
        )

        conversation_history.append({"role": "assistant", "content": response['choices'][0]['message']['content']}) # GPT 답변 message 입력
        return response['choices'][0]['message']['content'], conversation_history
    else:
        conversation_history.append({"role": "user", "content": message}) # 입력한 User의 message 입력
        time.sleep(2) # 바로 넘어가는게 자연스럽지 못해서 추가해놓음

        final_message = "알겠습니다. 다음 질문으로 넘어가겠습니다."

        conversation_history.append({"role": "assistant", "content": final_message}) # GPT 답변 message 입력
        return final_message, conversation_history
        
# 로컬 디렉토리에 대화문 전문 저장, 전체 대화 내용들을 구분자로 나누어 저장함
# + 텍스트 내 이슈가 될만한 pattern은 삭제처리
def del_pattern(x: dict, pattern_lst: list):
    """
    문자열에서 주어진 패턴을 삭제하는 함수입니다.

    :param x: 패턴을 삭제할 대상 딕셔너리
    :type x: dict
    :param pattern_lst: 삭제할 패턴의 리스트
    :type pattern_lst: list

    :return: 패턴이 삭제된 대상 딕셔너리
    :rtype: dict
    """
    for pattern in pattern_lst:
        x['content'] = x['content'].replace(pattern, "'")
    return x
    
def preprocessing_conversation_history(conversation_history):
    """
    대화 기록에서 특정 패턴을 삭제하는 전처리 함수입니다.

    :param conversation_history: 대화 기록을 담고 있는 리스트
    :type conversation_history: list

    :return: 패턴이 삭제된 대화 기록
    :rtype: list
    """
    del_pattern_lst = ["<", ">"]
    conversation_history = [[del_pattern(n, del_pattern_lst) for n in lst if type(n)!=type(None)]
                                                                            for lst in conversation_history]
    return conversation_history

def save_conversation_history(ALL_CONVERSATION_SAVE_DIR,all_conversation_history):
    with open(ALL_CONVERSATION_SAVE_DIR, 'w', encoding='utf-8') as f:
        for conversation in all_conversation_history:  # 대질문 대화별
            for message in conversation:                                # 대질문 대화 내 문장 별 저장
                f.write(f"{message['role']}: {message['content']}\n")
            f.write("\n\n$$$$$$$$$$\n\n")    