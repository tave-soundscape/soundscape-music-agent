from langchain_openai import ChatOpenAI
from music_agent import config

model = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    streaming=True,
    api_key=config.OPENAI_API_KEY
)