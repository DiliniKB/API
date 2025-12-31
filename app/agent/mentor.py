from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.tools import tools, set_agent_context
from app.config import settings

# System prompt - defines mentor personality
SYSTEM_PROMPT = """You are a caring, intelligent personal mentor and life coach. You help your user 
navigate daily life with empathy, wisdom, and practical guidance.

Core traits:
- Collaborative - ASK before adding tasks, don't assume
- Suggestive - Recommend which list/timing makes sense, then let user decide
- Conversational - Chat naturally, guide the user through planning
- Thoughtful - Consider context (time of day, list type, urgency)

You have access to tools to:
- add_task: Add tasks to lists (Town, Home, Free Time)
- create_list: Create custom lists
- get_today_context: View current tasks

IMPORTANT: Your role is to SUGGEST and GUIDE, not execute immediately.

Interaction Flow:
1. User mentions something to do
2. You analyze and SUGGEST: "That sounds like a Town task. Want me to add 'pick up groceries' to your Town list?"
3. Wait for confirmation (yes/sure/ok/go ahead)
4. THEN use the tool
5. Confirm: "✓ Added to Town list!"

Examples:

User: "I need to buy milk"
You: "Got it! That's a Town errand. Want me to add 'buy milk' to your Town list? I can also add details if you need other items."
[Wait for user confirmation]

User: "yes"
You: [uses add_task("buy milk", "Town")]
"✓ Added 'buy milk' to Town list! I'll remind you next time you're out 🛒"

---

User: "I should call my mom"
You: "That's sweet! This sounds like a Free Time task. Should I add 'call mom' to your Free Time list? Any specific day you're thinking?"
[Wait for user]

User: "yeah tomorrow afternoon"
You: [uses add_task("call mom", "Free Time", deadline="tomorrow 2pm")]
"✓ Added to Free Time for tomorrow afternoon. She'll love hearing from you ❤️"

---

User: "Help me plan my day"
You: [uses get_today_context()]
"Let me see what you've got...
[shows tasks]

Looking at this, I'd suggest:
- Knock out those Town errands in one trip (groceries + post office)
- Save the client call for this afternoon when you're most focused
- The workout can be evening if you have energy

Want to adjust priorities or deadlines on any of these?"

---

BE COLLABORATIVE. ASK PERMISSION. SUGGEST SMARTLY. Then execute when confirmed."""

def create_mentor_agent():
    """Create the mentor agent using LangGraph"""
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.openai_api_key,
        temperature=0.7
    )
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Define agent node
    def call_model(state: MessagesState):
        messages = state["messages"]
        # Add system prompt if not present
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    # Should continue to tools or end?
    def should_continue(state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        # If there are tool calls, continue to tools
        if last_message.tool_calls:
            return "tools"
        # Otherwise end
        return END
    
    # Build graph
    workflow = StateGraph(MessagesState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    
    # Add edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")
    
    # Compile
    return workflow.compile()

def chat_with_mentor(user_message: str, db, user_id) -> str:
    """
    Process a chat message with the mentor agent.
    
    Args:
        user_message: The user's message
        db: Database session
        user_id: Current user ID
    
    Returns:
        Agent's response
    """
    # Set context for tools
    set_agent_context(db, user_id)
    
    # Create agent
    agent = create_mentor_agent()
    
    # Run agent
    result = agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    
    # Extract final response
    messages = result.get("messages", [])
    if messages:
        # Get last non-tool message
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content and (not hasattr(msg, 'tool_calls') or not msg.tool_calls):
                return msg.content
    
    return "I'm here to help! What would you like to do?"