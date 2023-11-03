import langchain
import langsmith
import streamlit

from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, GroupChatManager

###


config_list=[{
    'model': 'gpt-3.5-turbo-16k',
    'api_key': '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'
}]
llm_config={
    'request_timeout':600,
    'seed':42,
    'config_list':config_list,
    'temperature':0   
}

assistant= AssistantAgent(
    name="Psychotherapy",
    llm_config=llm_config,
    system_message=""
)
user_proxy=UserProxyAgent(
    llm_config=llm_config,
    name="UserProxyAgent",
    human_input_mode='TERMINATE',
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda msg: msg.get("content","").rstrip().endswith("TERMINATE"),
    code_execution_config={'work_dir': 'web', },
    system_message="""
"""
)

task="HI"

""" user_proxy.initiate_chat(
    recipient=assistant,
    message=task
) """
config_list = config_list_from_json(
"OAI_CONFIG_LIST")
config_list = config_list_from_json(
env_or_file="OAI_CONFIG_LIST",
file_location=".",
)
print(config_list)