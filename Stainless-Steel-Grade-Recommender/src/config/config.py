import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


class Config:

    GROQ_API_KEY=os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]

    TAVILY_API_KEY=os.getenv("TAVILY_API_KEY") or st.secrets["TAVILY_API_KEY"]

    LLM_MODEL="llama-3.3-70b-versatile"

    EVALUATOR_MODEL="llama-3.1-8b-instant"

    EMBEDDING_MODEL="all-MiniLM-L6-v2"

    CHUNK_SIZE=1200

    CHUNK_OVERLAP=200

    @classmethod
    def validate(cls):

        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY missing")

        if not cls.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY missing")

    @classmethod
    def get_llm(cls):

        cls.validate()

        os.environ["TAVILY_API_KEY"]=cls.TAVILY_API_KEY

        return ChatGroq(
            model=cls.LLM_MODEL,
            api_key=cls.GROQ_API_KEY,
            temperature=0
        )

    @classmethod
    def get_evaluator_llm(cls):

        cls.validate()

        return ChatGroq(
            model=cls.EVALUATOR_MODEL,
            api_key=cls.GROQ_API_KEY,
            temperature=0
        )