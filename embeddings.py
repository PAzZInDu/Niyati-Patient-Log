from openai import OpenAI
import streamlit as st
import os


os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["OPENAI_API_KEY"]
TEXT_MODEL = "text-embedding-3-large"

# create client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def get_openai_embeddings(text: str) -> list[float]:
    response = client.embeddings.create(
        input=f"{text}",
        model=TEXT_MODEL,
        dimensions=256
        )

    return response.data[0].embedding