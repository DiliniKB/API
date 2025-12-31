from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.agent.tools import tools, set_agent_context
from app.config import settings
from app.models import Message

# System prompt - defines mentor personality for new entity system
SYSTEM_PROMPT = """You are a caring, intelligent personal mentor and life coach.

You help users manage their life using an entity system where everything 
(tasks, events, goals) has context tags like:
- work, meeting, focus_required
- town, home, shopping
- personal, health, social

You have tools:
- add_entity(title, entity_type, context_tags, ...) - Add tasks/events
- get_entities_overview() - See what user has

WORKFLOW:
1. When user mentions something to do, determine:
   - Is it a task (flexible timing) or event (fixed time)?
   - What context? (work/town/home/personal)
   - Any deadline mentioned?

2. Suggest: "Sounds like [context]. Should I add '[title]'?"

3. After confirmation, use tool with appropriate context tags

4. Confirm what you created

Be conversational. Ask clarifying questions. Explain your reasoning.
Context tags help batch similar activities (e.g., all town errands together).

Current date: {current_datetime}
User timezone: {user_timezone}
"""

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
    Includes conversation history for context.
    
    Args:
        user_message: The user's message
        db: Database session
        user_id: Current user ID
    
    Returns:
        Agent's response
    """
    # Set context for tools
    set_agent_context(db, user_id)
    
    # Load recent conversation history (last 20 messages)
    recent_messages = db.query(Message).filter(
        Message.user_id == user_id
    ).order_by(Message.created_at.desc()).limit(20).all()
    
    # Build message history
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    
    # Add conversation history (reverse to get chronological order)
    for msg in reversed(recent_messages):
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))
    
    # Add current user message
    messages.append(HumanMessage(content=user_message))
    
    # Create and run agent
    agent = create_mentor_agent()
    
    result = agent.invoke({
        "messages": messages
    })
    
    # Extract final response
    response_messages = result.get("messages", [])
    if response_messages:
        # Get last non-tool message
        for msg in reversed(response_messages):
            if hasattr(msg, 'content') and msg.content and (not hasattr(msg, 'tool_calls') or not msg.tool_calls):
                return msg.content
    
    return "I'm here to help! What would you like to do?"