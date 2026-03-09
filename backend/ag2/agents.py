"""
ag2/agents.py — AG2 agent definitions
"""
import sys, os

import autogen
from app.api.config import API_BASE, API_KEY, MODEL
from prompts.agent_prompts import TRIAGE_PROMPT, CLARIFICATION_PROMPT, SQL_PROMPT_TEMPLATE
from ag2.tools import get_schema_info

llm_config = {
    "config_list": [{
        "model":    MODEL,
        "api_key":  API_KEY,
        "base_url": API_BASE + "/v1",
    }],
    "temperature": 0,
}

_SCHEMA_CACHE = None

def get_cached_schema():
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is None:
        _SCHEMA_CACHE = get_schema_info()
    return _SCHEMA_CACHE


def make_triage_agent():
    return autogen.AssistantAgent(
        name="triage_agent",
        llm_config=llm_config,
        system_message=TRIAGE_PROMPT,
    )


def make_clarification_agent():
    return autogen.AssistantAgent(
        name="clarification_agent",
        llm_config=llm_config,
        system_message=CLARIFICATION_PROMPT,
    )


def make_sql_agent():
    schema = get_cached_schema()
    return autogen.AssistantAgent(
        name="sql_agent",
        llm_config=llm_config,
        system_message=SQL_PROMPT_TEMPLATE.format(schema=schema),
    )