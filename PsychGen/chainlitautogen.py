import openai
import json, ast
import os
import chainlit as cl
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, GroupChat, GroupChatManager

MAX_ITER = 5


@cl.on_chat_start
async def agent_setup():
    config_list = config_list_from_json(
    "OAI_CONFIG_LIST")
    config_list = config_list_from_json(
    env_or_file="OAI_CONFIG_LIST",
    file_location=".",
    )

    general_llm_config={
        'request_timeout':600,
        'seed':42,
        'config_list':config_list,
        'temperature':0   
    }

    psychotherapist= AssistantAgent(
        name="PsychoTherapist",
        llm_config=general_llm_config,
        system_message="""
        Expertise: Psychotherapy

        Goals:

        1. Offer compassionate psychotherapy services.
        2. Collaborate with @CognoTherapist to understand user emotions.
        3. Provide personalized coping strategies.
        4. Generate user profiles in coordination with @CognoTherapist.
        
        Approach:

        1. Utilizes various psychotherapy modalities.
        2. Collaborates with @CognoTherapist to create user profiles and understand emotional patterns.
        3. Tailors strategies for coping with negative feelings.
        4. Coordinates with @CognoTherapist to identify triggers.
        5. Engages in discussions with @CognoTherapist to adapt user profiles based on new information.
        6. Collaboratively determines the most effective questions to improve the user profile, offering suggestions alongside and pass it to @Coordinator.
"""
        
        
        
    )
    cognotherapist= AssistantAgent(
        name="CognoTherapist",
        llm_config=general_llm_config,
        system_message="""
        Expertise: Cognitive Behavioral Therapy (CBT)

            Goals:

            1. Provide targeted CBT interventions.
            2. Collaborate with @PsychoTherapist to understand user emotions.
            3. Offer precise emotional analysis and coping strategies.
            4. Suggest music and video content for emotional support.
            
            Approach:

            1. Employs AI for emotional analysis.
            2. Collaborates with @PsychoTherapist to create user profiles.
            3. Offers detailed emotional insights.
            4. Recommends music and videos for coping.
            5. Engages in discussions with @PsychoTherapist to adapt user profiles based on new information.
            6. Together with MindfulHealer, determines the most effective questions for improving the user profile, providing relevant suggestions and pass it to @Coordinator.
            7. If you are satisfied with data gathered from interacting with the UserProxyAgent TERMINATE and create a text file working dir with User profile in it.
        
        """
          
    )
    profilegenius=AssistantAgent(
        name="ProfileGenius",
        system_message="""
            Expertise: User Profile Generation

            Goals:
            1. Collaborate with @CognoTherapist and @PsychoTherapist to create comprehensive user profiles.
            2. Analyze and compile user data to generate a text-based user profile and Create a text file and save it.
            3. Ensure user privacy and data security in the profile creation process.

            Approach:

            1. Integrates data from @CognoTherapist and @PsychoTherapist to build accurate user profiles.
            2. Utilizes AI-driven algorithms to compile user data into a structured text format.
            3. Adheres to strict privacy and security protocols to protect user information.
            
            User Profile Creation:

            1. Receives data from @CognoTherapist and @PsychoTherapist to create user profiles.
            2. Generates a txt file with user profile, including demographic information, emotional insights, and coping strategies.
            3. Ensures the profile is stored securely and is only accessible by authorized personnel.
        """,
        llm_config=general_llm_config
    )
    user_proxy=UserProxyAgent(
        name="UserProxyAgent",
        human_input_mode='NEVER',
        is_termination_msg=lambda msg: msg.get("content","").rstrip().endswith("TERMINATE"),
        code_execution_config={'work_dir': 'User_Profile' },
        llm_config=general_llm_config
        )
    group_chat= GroupChat(
        agents=[user_proxy,cognotherapist,psychotherapist,profilegenius],
        messages=[]
    )
    manager=GroupChatManager(
        groupchat=group_chat,
        llm_config=general_llm_config
    )
    cl.user_session.set('manager', manager)
    cl.user_session.set('user_proxy', user_proxy)
    await cl.Message(content=f"Start chatting with PhysGen").send()


@cl.on_message
async def run_conversation(msg: cl.Message):
    # check if user message changed
    user_message = msg.content
    if user_message == cl.user_session.get('user_message'):
        return
    manager = cl.user_session.get('manager')
    user_proxy = cl.user_session.get('user_proxy')
    cur_iter = 0

    while cur_iter < MAX_ITER:
        if len(manager.chat_messages[user_proxy]) == 0 :
            print('initiating chat')
            user_proxy.initiate_chat(
                manager,
                message=user_message,
            )
        else:
            print('FOLLOW up message')
            # followup of the previous question
            user_proxy.send(
                recipient=manager,
                message=user_message,
            )
        message_history = manager.chat_messages[user_proxy]
        last_seen_message_index = cl.user_session.get('last_seen_message_index', 0)
        print(message_history)
        for message in message_history[last_seen_message_index+1:]:
            await cl.Message(author=message["role"], content=message["content"]).send()
        cl.user_session.set('last_seen_message_index', len(message_history))

        cur_iter += 1
        return