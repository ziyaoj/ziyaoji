import streamlit as st
from router import route_question

# ========== 标题 + 垃圾桶按钮放在同一行 ==========
col1, col2 = st.columns([9, 1])
with col1:
    st.title("校园问答调度系统 MVP")
with col2:
    st.write("")  # 占位，让按钮垂直居中对齐标题
    if st.button("🗑️", help="清除对话历史"):
        st.session_state.chat_history = []
        st.session_state.messages_display = []
        st.rerun()

# ========== 会话状态初始化 ==========
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "messages_display" not in st.session_state:
    st.session_state.messages_display = []

# 显示历史对话
for msg in st.session_state.messages_display:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "meta" in msg:
            st.caption(f"路由: {msg['meta']['route']} | 耗时: {msg['meta']['response_time']:.2f}s")

# 输入框
question = st.chat_input("请输入你的问题")

if question:
    # 展示用户问题
    st.session_state.messages_display.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # 调用路由，传入对话历史
    answer, meta = route_question(question, history=st.session_state.chat_history)

    # 更新对话历史
    st.session_state.chat_history.append({"role": "user", "content": question})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # 只保留最近 6 条记录（3 轮）
    if len(st.session_state.chat_history) > 6:
        st.session_state.chat_history = st.session_state.chat_history[-6:]

    # 展示回答
    st.session_state.messages_display.append({"role": "assistant", "content": answer, "meta": meta})
    with st.chat_message("assistant"):
        st.write(answer)
        st.caption(f"路由: {meta['route']} | 耗时: {meta['response_time']:.2f}s")