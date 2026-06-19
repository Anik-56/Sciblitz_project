# app.py
import streamlit as st
from groq import Groq

client = Groq(api_key="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")

st.title("Sciblitz 🔬")
st.caption("Powered by LLaMA 3.3 70B — Free & Fast")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input
if prompt := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # free & very smart
                messages=st.session_state.messages,
                max_tokens=1024,
            )
            reply = response.choices[0].message.content
            st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})