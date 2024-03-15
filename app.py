import streamlit as st
import os
import requests

def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        for file in files:
            file_path = os.path.join(root, file)
            response = requests.get(f"http://localhost:8000/fileinfo/{file}")
            if response.status_code == 200:
                file_info = response.json()
                st.write(f"File: {file_path}, Size: {file_info['size']} bytes, Uploaded at: {file_info['uploaded_at']}")
            else:
                error_message = response.json().get('error', 'Unknown error')
                st.write(f"File: {file_path}, Error: {error_message}")

def items():
    response = requests.get("http://localhost:8000/items/")
    if response.status_code == 200:
        return response.json()
    else:
        return []

st.title('File Upload Tutorial')

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    file_details = {"filename": uploaded_file.name, "filebytes": uploaded_file.getbuffer()}
    response = requests.post("http://localhost:8000/create_upload_file", data=file_details)
    if response.status_code == 200:
        st.success("Saved File:{} to data".format(uploaded_file.name))
    else:
        st.error("Error saving file: {}".format(response.json()['detail']))

if st.button('Show Uploaded Files in data'):
    list_files('data')

if st.button('뭔지 모르겠는 버튼'):
    item_list = items()
    st.write(item_list)
    st.write(type(item_list[0]))
    for item in item_list:
        st.write(f"Item: {item}")
