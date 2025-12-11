from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-2024-11-20",
    temperature=0.0,
    streaming=True
)