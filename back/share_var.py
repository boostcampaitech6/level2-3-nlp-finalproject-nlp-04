# 변수 공유를 위한 함수들
import pickle


def get_shared_var(name):
    """
    주어진 이름에 해당하는 공유 변수를 가져옵니다.

    Parameters:
        name (str): 가져올 공유 변수의 이름

    Returns:
        object: 주어진 이름에 해당하는 공유 변수의 값. 만약 파일이 존재하지 않으면 None을 반환합니다.
    """
    try:
        with open("shared.pkl", "rb") as fp:
            shared = pickle.load(fp)
            return shared[name]
    except FileNotFoundError:
        return ''


def set_shared_var(name, value):
    """
    공유 변수를 설정하는 함수입니다.

    Parameters:
        name (str): 변수 이름
        value (Any): 변수 값

    Returns:
        None
    """
    shared = {name: value}
    with open("shared.pkl", "wb") as fp:
        pickle.dump(shared, fp)
