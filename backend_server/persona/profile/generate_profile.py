from typing import Dict, List

from backend_server.utils.llm import async_llm_function


@async_llm_function(prompt_file="generate_agent_profile_plan.md", usage="chat")
def generate_profiles_plan(
    scenario: str,
    request: str,
    agent_count: int,
) -> Dict[str, str]:
    """
    Generates a plan for each agent in brief natural language.
    """
    # This is a placeholder, the actual implementation is handled by the llm_function decorator
    return {}


@async_llm_function(prompt_file="generate_agent_profile.md", usage="chat")
def generate_profiles(
    plan: Dict[str, str],
) -> List[Dict]:
    """
    Generates a detailed structured profile for each agent.
    """
    # This is a placeholder, the actual implementation is handled by the llm_function decorator
    return [
        {
            "name": "Maria Rodriguez",
            "first_name": "Maria",
            "last_name": "Rodriguez",
            "age": 52,
            "innate": "Practical, resilient, empathetic",
            "daily_plan_req": "Isabella Rodriguez opens Hobbs Cafe at 8am everyday, and works at the counter until 8pm, at which point she closes the market.",
            "learned": "Over 30 years of experience selling vegetables at the local market. Knows everything about produce quality, pricing, and customer service. Experienced in managing finances and navigating market regulations. Deep understanding of local community needs and preferences. Familiar with traditional farming practices.",
            "currently": "Concerned about rising stall fees and increased competition from larger vendors. Worried about the lack of hygiene in the market affecting her customers' health and her reputation. Determined to maintain affordable prices for her regular customers and advocate for better market conditions. Looking for ways to improve her stall's hygiene and attract new customers.",
            "lifestyle": "Wakes up early to select the freshest produce from local farms. Spends the day at the market, interacting with customers and managing her stall. Returns home in the late afternoon to prepare meals and spend time with her family. Attends local community meetings and events. Enjoys gardening in her spare time.",
            "living_area": "Lives in a small, modest house in a working-class neighborhood near the market. The house is well-maintained but simple. The neighborhood is close-knit and diverse, with a strong sense of community. There is a small garden in the backyard where she grows some of her own vegetables.",
        }
    ]
