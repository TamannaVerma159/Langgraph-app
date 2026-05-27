#  this is an example o chatbot, which generate response , saves history and remembers the previous messages from the memory.
from typing_extensions import TypedDict
from typing import Annotated
import operator
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
# This allows the chatbot to remember previous conversations.

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# load gemini model
llm = ChatGroq(
    model= "llama-3.1-8b-instant",
    temperature= 0.7
)

# graph state
class ChatState(TypedDict):
    user_message :str
    history : Annotated[list[dict],operator.add]
# When new history is returned, append it instead of replacing it.
    response : str

# graph node
def chatbot_node(state:ChatState):
    user_message = state["user_message"]
    history = state["history"]
    # here we call the LLM to generate response based on the user message and history.
    
    messages = []
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    # add current user message
    messages.append(HumanMessage(content=user_message))

    # call gemini
    result = llm.invoke(messages)
    response = result.content
    return{
        "history"  :[
            {"role" : "user", "content" : user_message},
            {"role" : "assistant", "content" : response}
        ],
        "response" : response
    }

# build graph
builder = StateGraph(ChatState)
builder.add_node("chatbot",chatbot_node)
builder.add_edge(START,"chatbot")
builder.add_edge("chatbot",END)
checkpointer = InMemorySaver()
# create temporary storage
graph = builder.compile(checkpointer=checkpointer)

# thread configuration
config = {
    "configurable" : {
        "thread_id" : "user-1"
    }
}
result1 = graph.invoke(
    {
    "user_message" : "Hello, my name is tamanna",
    "history" : [],
    "response" : ""
    },
    config=config)
print("first response:")
print(result1["response"])
print("\nhistory:")
print(result1["history"])

result2 = graph.invoke(
    {
        "user_message" : "What is my name?",
        "history" : [],
        "response" : ""
    },
    config=config)  
print("\nsecond response:")
print(result2["response"])
print("\nUpdated history:")
print(result2["history"])