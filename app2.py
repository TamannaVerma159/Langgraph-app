#  this is an example o chatbot, which generate response , saves history and remembers the previous messages from the memory.
from typing_extensions import TypedDict
from typing import Annotated
import operator
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
# This allows the chatbot to remember previous conversations.

class ChatState(TypedDict):
    user_message :str
    history : Annotated[list[str],operator.add]
# When new history is returned, append it instead of replacing it.
    response : str
def chatbot_node(state:ChatState):
    user_message = state["user_message"]
    response = f"You said: {user_message}"
    return{
        "history"  :[F"User said: {user_message}",f"Bot: {response}"],
        "response" : response
    }
builder = StateGraph(ChatState)
builder.add_node("chatbot",chatbot_node)
builder.add_edge(START,"chatbot")
builder.add_edge("chatbot",END)
checkpointer = InMemorySaver()
# create temporary storage
graph = builder.compile(checkpointer=checkpointer)

config = {
    "configurable" : {
        "thread_id" : "user-1"
    }
}
result1 = graph.invoke(
    {
    "user_message" : "Hello, how are you?",
    "history" : [],
    "response" : ""
    },
    config=config)
print("first response:")
print(result1["response"])
print("history:")
print(result1["history"])

result2 = graph.invoke(
    {
        "user_message" : "What is the weather like today?",
        "history" : [],
        "response" : ""
    },
    config=config)  
print("\nsecond response:")
print(result2["response"])
print("history:")
print(result2["history"])