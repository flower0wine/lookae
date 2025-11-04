from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest


@dataclass
class ContextSchema:
    user_name: str

@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:  
    user_name = request.runtime.context.user_name
    return f"You are a helpful assistant. Address the user as {user_name}."

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[get_weather],
    middleware=[personalized_prompt],
    context_schema=ContextSchema
)

agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
    context=ContextSchema(user_name="John Smith")  
)