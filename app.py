# app.py (minimal)
import streamlit as st
from llama_cpp import Llama

MODEL_PATH = "E:\models\llama-2-7b.Q4_K_M.gguf"  # <-- set your model file here

@st.cache_resource
def load_model():
    return Llama(model_path=MODEL_PATH)

llm = Llama(
    model_path=MODEL_PATH,
    n_threads=12,       # match your CPU cores
    n_ctx=2048,         # context window size
    verbose=True
)

st.title("Sciblitz — Simple Chat")
prompt = st.text_input("Ask something:")

if prompt:
    try:
        out = llm(prompt, max_tokens=150)
        st.write(out["choices"][0]["text"])
    except Exception as e:
        st.error(f"Model error: {e}")
