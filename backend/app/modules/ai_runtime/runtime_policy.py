from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.modules.ai_runtime.models import AITask
from backend.app.modules.ai_runtime.providers.base import RuntimePolicyBundle
from backend.app.modules.prompt_skill.models import PromptVersion, SkillVersion
from backend.app.modules.prompt_skill.registry_loader import compute_content_hash


class RuntimePolicyInvalidError(RuntimeError):
    pass


def compile_runtime_policy(session: Session, ai_task: AITask) -> RuntimePolicyBundle:
    prompt = session.get(PromptVersion, ai_task.prompt_version_id)
    skill = session.get(SkillVersion, ai_task.skill_version_id)
    if prompt is None or skill is None:
        raise RuntimePolicyInvalidError("Prompt or skill version does not exist.")
    if prompt.status != "active" or skill.status != "active":
        raise RuntimePolicyInvalidError("Prompt and skill versions must be active.")
    if prompt.hash != compute_content_hash(prompt.content):
        raise RuntimePolicyInvalidError("Prompt content hash does not match its published version.")
    if skill.hash != compute_content_hash(skill.content):
        raise RuntimePolicyInvalidError("Skill content hash does not match its published version.")
    if prompt.agent_name != ai_task.agent_name:
        raise RuntimePolicyInvalidError("Prompt version is not assigned to this agent.")
    if ai_task.agent_name not in skill.applicable_agents:
        raise RuntimePolicyInvalidError("Skill version is not applicable to this agent.")

    return RuntimePolicyBundle(
        agent_name=ai_task.agent_name,
        prompt_name=prompt.name,
        prompt_version=prompt.version,
        prompt_hash=prompt.hash,
        prompt_content=prompt.content,
        input_schema_json=dict(prompt.input_schema_json),
        output_schema_json=dict(prompt.output_schema_json),
        skill_name=skill.name,
        skill_version=skill.version,
        skill_hash=skill.hash,
        skill_content=skill.content,
        quality_gates=list(skill.quality_gates_json),
        forbidden_actions=list(skill.forbidden_actions_json),
        tool_permissions=list(skill.tool_permissions_json),
    )
