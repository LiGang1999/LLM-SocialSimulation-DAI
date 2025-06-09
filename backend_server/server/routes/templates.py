import json
import os
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from backend_server.server.auth import get_current_active_user, get_current_user
from backend_server.server.routes.simulation import is_template_public, user_owns_template
from backend_server.server.schemas import User
from backend_server.utils import config
from backend_server.utils.logs import L

router = APIRouter()
STORAGE_PATH = config.storage_path


def load_json_file(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        L.error(f"Invalid JSON in file: {file_path}")
        return {}
    except FileNotFoundError:
        L.error(f"File not found: {file_path}")
        return {}


def get_public_templates():
    """Get list of available public templates"""
    public_path = os.path.join(STORAGE_PATH, "public_templates")
    public_templates = []
    if os.path.exists(public_path):
        public_dirs = [dir for dir in os.listdir(public_path) if os.path.isdir(os.path.join(public_path, dir))]
        for dir in public_dirs:
            template_meta_file = os.path.join(public_path, dir, "reverie", "meta.json")
            template_meta = load_json_file(template_meta_file)
            if template_meta:
                hidden = template_meta.get("hidden", True)
                if not hidden:
                    public_templates.append(template_meta)

    # Sort templates
    def sort_key(env):
        sim_code = env.get("template_sim_code", "")
        return (0 if "online" in sim_code.lower() else 1, sim_code)

    public_templates.sort(key=sort_key)
    return public_templates


@router.get("/fetch_templates")
async def fetch_templates(current_user: User = Depends(get_current_user(False), use_cache=False)):
    # Get public templates
    public_templates = get_public_templates()

    # If user is not authenticated, return only public templates
    if current_user is None:
        return {"public_templates": public_templates, "user_templates": []}

    # Get user templates from storage_path/{user_hash}/
    from backend_server.utils import get_user_hash

    user_hash = get_user_hash(current_user.username)
    user_path = os.path.join(STORAGE_PATH, "user_templates", user_hash)
    user_templates = []
    if os.path.exists(user_path):
        user_dirs = [dir for dir in os.listdir(user_path) if os.path.isdir(os.path.join(user_path, dir))]
        for dir in user_dirs:
            template_meta_file = os.path.join(user_path, dir, "reverie", "meta.json")
            template_meta = load_json_file(template_meta_file)
            if template_meta:
                user_templates.append(template_meta)

    # Sort user templates
    def sort_key(env):
        sim_code = env.get("template_sim_code", "")
        return (0 if "online" in sim_code.lower() else 1, sim_code)

    user_templates.sort(key=sort_key)

    return {"public_templates": public_templates, "user_templates": user_templates}


@router.delete("/delete_template")
async def delete_template(sim_code: str, current_user: User = Depends(get_current_active_user)):
    """Delete a user template"""
    if not sim_code:
        raise HTTPException(status_code=400, detail="Missing sim_code parameter")

    # Check if template is public (can't delete public templates)
    if is_template_public(sim_code):
        raise HTTPException(status_code=403, detail="Cannot delete public templates")

    # Check if user owns the template
    if not user_owns_template(current_user.username, sim_code):
        raise HTTPException(status_code=403, detail="You don't own this template")

    # Delete the template directory
    from backend_server.utils import get_user_hash

    user_hash = get_user_hash(current_user.username)
    template_path = os.path.join(STORAGE_PATH, "user_templates", user_hash, sim_code)

    try:
        if os.path.exists(template_path):
            import shutil

            shutil.rmtree(template_path)
            return {"status": "success", "message": "Template deleted"}
        else:
            raise HTTPException(status_code=404, detail="Template not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch_template")
async def fetch_template(sim_code: str, current_user: User = Depends(get_current_active_user)):
    if not sim_code:
        raise HTTPException(status_code=400, detail="Missing sim_code parameter")

    # Check if the template is accessible to the user
    # First, check if it's a public template
    if is_template_public(sim_code):
        env_path = os.path.join(STORAGE_PATH, "public_templates", sim_code)
    # Then check if it's owned by the user
    elif user_owns_template(current_user.username, sim_code):
        from backend_server.utils import get_user_hash

        user_hash = get_user_hash(current_user.username)
        env_path = os.path.join(STORAGE_PATH, "user_templates", user_hash, sim_code)
    else:
        # Template doesn't exist or user doesn't have access
        raise HTTPException(status_code=403, detail="Template not found or access denied")

    meta_file = os.path.join(env_path, "reverie", "meta.json")
    env_meta = load_json_file(meta_file)

    persona_names = env_meta.get("persona_names", [])
    persona_info = {}
    for persona in persona_names:
        scratch_file = os.path.join(env_path, "personas", persona, "bootstrap_memory", "scratch.json")
        scratch_data = load_json_file(scratch_file)
        persona_info[persona] = {
            "name": scratch_data.get("name", ""),
            "first_name": scratch_data.get("first_name", ""),
            "last_name": scratch_data.get("last_name", ""),
            "age": scratch_data.get("age", 0),
            "daily_plan_req": scratch_data.get("daily_plan_req", ""),
            "innate": scratch_data.get("innate", ""),
            "learned": scratch_data.get("learned", ""),
            "currently": scratch_data.get("currently", ""),
            "lifestyle": scratch_data.get("lifestyle", ""),
            "living_area": scratch_data.get("living_area", ""),
            "bibliography": "",  # WIP
        }

    events_file = os.path.join(env_path, "reverie", "events.json")
    events = load_json_file(events_file)
    workflow = env_meta.get("workflow", {})

    return {"meta": env_meta, "personas": persona_info, "events": events, "workflow": workflow}
