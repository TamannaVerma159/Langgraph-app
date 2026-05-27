# human in the loop workflow
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import  interrupt, Command

# definw state
class RefundState(TypedDict):
    customer_name: str
    refund_amount: int
    appoved: bool
    final_status: str

# node- check if approval is needed
def check_refund_request(state: RefundState):
    amount = state["refund_amount"]

    if amount <= 1000:
        return {
            "appoved" : True,
            "final_status" : "Small refund amount : auto-approved"
        }
    return{
        "final_status": "Large refund requires human approval."
    }

# human approval node
def human_approval_node(state:RefundState):
    if state["refund_amount"] <= 1000:
        return {}
    
    # interrupt function pauses the function execution and waits for the human input, and once the human input is provided , it resumes the execution.
    human_decision = interrupt({
        "message" : "Approval required",
        "customer_name": state["customer_name"],
        "refund_amount": state["refund_amount"],
        "question": "Should we approved this refund?"
    })
    return{
        "approved": human_decision["approved"]
    }

# final processing node
def process_refund(state: RefundState):
    if state["appoved"]:
        return {
            "final_status": f"Refund of ₹{state['refund_amount']} has been approved. "
        }
            
    return { 
        "final_status": f"Refund of ₹{state['refund_amount']} has been rejected."
            }

# build graph
builder = StateGraph(RefundState)
builder.add_node("check_refund_request", check_refund_request)
builder.add_node("human_approval_node", human_approval_node)
builder.add_node("process_refund", process_refund)

builder.add_edge(START, "check_refund_request")
builder.add_edge("check_refund_request", "human_approval_node")
builder.add_edge("human_approval_node", "process_refund")
builder.add_edge("process_refund", END)

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)

# run graph
config = {
    "configurable" : {
        "thread_id" : "refund-thread-1"
    }
}
first_result = graph.invoke(
    {
        "customer_name" : "John Doe",
        "refund_amount" : 5000,
        "appoved" : False,
        "final_status" : ""
    },
    config=config
)
print("Graph paused for human approval")
print(first_result)

final_result = graph.invoke(
    Command(resume= {"approved": True}),
    config=config
)
print("\nFinal result:")
print(final_result["final_status"])
# LangGraph - Build Stateful AI applications.
# LangGraph Core Components - State, Nodes, Edges

# Supervisor / Manager / Coordinator Agent
# In a multi-agent AI application, one agent generally acts like a Coordinator Agent, whose responsibility is to make sure to call the correct/specialized agent for a particular task.