from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

# Import the openai api key
config_list = config_list=[{
    'model': 'gpt-3.5-turbo-16k',
    'api_key': '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'
}]

# Create assistant agent
assistant = AssistantAgent(name="assistant", llm_config={
                           "config_list": config_list})

# Create user proxy agent
user_proxy = UserProxyAgent(
    name="user_proxy",
    code_execution_config={"work_dir": "coding"})

# Start the conversation
user_proxy.initiate_chat(
    assistant, message="Plot a chart of NVDA, AAPL and TESLA stock price change YTD.")