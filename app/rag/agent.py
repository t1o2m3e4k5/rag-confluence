from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model
from app.config import get_settings
from .retrieval import retrieve

_settings = get_settings()

_llm = init_chat_model(_settings.llm_model_name, model_provider="openai")
_memory = MemorySaver()
_agent = create_react_agent(_llm, [retrieve], checkpointer=_memory)

SYSTEM_MESSAGE = {
    "role": "system",
    "content": "Always say \"thanks for asking!!\" at the end of the answer."
}

def stream_answer(prompt: str, thread_id: str):
    cfg = {"configurable": {"thread_id": thread_id}}
    user_message = {"role": "user", "content": prompt}
    messages = [SYSTEM_MESSAGE, user_message]
    for event in _agent.stream({"messages": messages}, stream_mode="values", config=cfg):
        yield event["messages"][-1]