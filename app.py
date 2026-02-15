import streamlit as st
from router import route_question

st.title("校园问答调度系统 MVP")

question = st.text_input("请输入你的问题")

if st.button("提交") and question:
    answer, meta = route_question(question)
    st.write("答案：")
    st.write(answer)
    st.json(meta)
