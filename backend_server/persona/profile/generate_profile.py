from typing import Dict, List

from backend_server.utils.llm import async_llm_function


@async_llm_function(prompt_file="generate_agent_profile_plan.md")
async def generate_profiles_plan(
    scenario: str,
    request: str,
    agent_count: int,
) -> Dict[str, str]:
    """
    Generates a plan for each agent in brief natural language.
    """
    # This is a placeholder, the actual implementation is handled by the llm_function decorator
    return {}


@async_llm_function(prompt_file="generate_agent_profile.md")
async def generate_profiles(
    plan: Dict[str, str],
) -> List[Dict]:
    """
    Generates a detailed structured profile for each agent.
    """
    # This is a placeholder, the actual implementation is handled by the llm_function decorator
    return []
