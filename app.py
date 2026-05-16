from typing_extensions import TypedDict
# typedict defines the structure of SataeGraph
from langgraph.graph import StateGraph, START, END

# define state of the application
class SupportedState(TypedDict):
    user_query : str
    category : str
    answer : str
    
# node-1
# user_query = when will i get my refund?
def classify_query(state: SupportedState):
    query = state["user_query"].lower()

    if "refund" in query:
        category = "refund"
    elif "return" in query or "returns" in query:
        category = "return"
    elif "shipping" in query  or "delivery" in query or "delivered" in query:
        category = "delivery"
    else:
        category = "general"
    
    return {"category" : category}
# node-2
def answer_query(state: SupportedState):
    category = state["category"]
    query = state["user_query"]

    # here, we should call the LLM with RAG to answer the user query basedon the company's knowledge base.
    answer = ""
    if category =="return":
        answer = "you can return the product with in 7 days of delivery"
    elif category == "refund":
        answer = "Refund wil be processed in 5-7 working days."
    elif category == "delivery":
        answer = "orders generally delivered with in 3-5 days."
    else: 
        answer = "For any other general query ,please call our customer care."
    return {"answer" : answer}

# Build the graph.
builder = StateGraph(SupportedState)

# add nodes.
builder.add_node("classify_query", classify_query)
builder.add_node("answer_query", answer_query)

# add  edges
builder.add_edge(START, "classify_query")
builder.add_edge("classify_query","answer_query")
builder.add_edge("answer_query", END)

graph = builder.compile()

# run the graph
result = graph.invoke(
    {
        "user_query" : "when my order will be delivered",
        "category" : "",
        "answer" : ""
    }
)

print(result)
