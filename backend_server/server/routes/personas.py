import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from backend_server.persona.profile.generate_profile import generate_profiles, generate_profiles_plan
from backend_server.reverie import ScratchData
from backend_server.server.auth import get_current_active_user
from backend_server.server.routes.simulation import get_reverie_instance
from backend_server.server.schemas import ProfilePlanReq, ProfilesReq, User
from backend_server.utils import config
from backend_server.utils.logs import L

router = APIRouter()
STORAGE_PATH = config.storage_path


@router.post("/generate_profiles_plan")
async def generate_profiles_plan_endpoint(req: ProfilePlanReq, current_user: User = Depends(get_current_active_user)):
    """Generate a plan for multiple profiles based on a description"""
    try:
        plan = await generate_profiles_plan(req.scenario, req.request, req.agent_count)
        return plan
    except Exception as e:
        L.error(f"Error generating profile plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating profile plan: {str(e)}")


@router.post("/generate_profiles")
async def generate_profiles_endpoint(req: ProfilesReq, current_user: User = Depends(get_current_active_user)):
    """Generate multiple profiles based on descriptions"""
    try:
        profiles = await generate_profiles(req.plan)
        return {"profiles": profiles}
    except Exception as e:
        L.error(f"Error generating profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating profiles: {str(e)}")


@router.get("/get_persona/{sim_code}")
async def get_persona(sim_code: str, current_user: User = Depends(get_current_active_user)):
    reverie_instance = get_reverie_instance(current_user.username, sim_code)
    personas_path = os.path.join(STORAGE_PATH, reverie_instance.template_sim_code, "personas")
    persona_names = set(
        name
        for name in os.listdir(personas_path)
        if os.path.isdir(os.path.join(personas_path, name)) and not name.startswith(".")
    )

    return {"personas": list(persona_names)}


@router.get("/personas_info")
async def personas_info(sim_code: str, current_user: User = Depends(get_current_active_user)):
    reverie_instance = get_reverie_instance(current_user.username, sim_code)
    r = reverie_instance.reverie
    persona_info = []

    try:
        for persona_name, persona in r.personas.items():
            scratch = persona.scratch
            persona_info.append(
                {
                    "name": persona_name,
                    "first_name": scratch.first_name,
                    "last_name": scratch.last_name,
                    "age": scratch.age,
                    "innate": scratch.innate,
                    "learned": scratch.learned,
                    "currently": scratch.currently,
                    "lifestyle": scratch.lifestyle,
                    "living_area": scratch.living_area,
                    "act_event": scratch.act_event,
                }
            )
    except ValidationError as e:
        L.warning(f"Error parsing persona {persona}: {e}")

    return {"personas": persona_info}


@router.get("/persona_detail")
async def persona_detail(sim_code: str, agent_name: str, current_user: User = Depends(get_current_active_user)):
    r = get_reverie_instance(current_user.username, sim_code)
    r = r.reverie
    persona_path = os.path.join(STORAGE_PATH, r.template_sim_code, "personas", agent_name)
    scratch = r.personas[agent_name].scratch
    scratch_data = vars(scratch)

    try:
        person = ScratchData(**scratch_data)
        persona_detail = person.dict()
    except ValidationError as e:
        L.warning(f"Error parsing persona {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing persona data for {agent_name}")

    return {"scratch": persona_detail, "a_mem": {}, "s_mem": {}}
