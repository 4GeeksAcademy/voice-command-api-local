import json
import logging
import re
from typing import Any

import httpx
from groq import AsyncGroq
from pydantic import ValidationError

from src.app.api.routes import tasks as task_routes
from src.app.core.config import get_settings
from src.app.schemas.voice import (
    InstructionPayload,
    TaskCreate,
    TaskReplace,
    TaskUpdate,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a voice-command router for a task list.
Return only a JSON object with exactly these keys: endpoint, method, params.
Do not include markdown or explanatory text.

Supported routes:
- List tasks: GET /tasks with empty params.
- Create a task: POST /tasks with title and optional done in params.
- Replace a task: PUT /tasks/{id} with title and done in params.
- Partially update a task: PATCH /tasks/{id} with only changed fields in params.
- Delete a task: DELETE /tasks/{id} with empty params.

For a task-specific operation, use the matching integer id from current_tasks.
Use uppercase HTTP methods. Never invent endpoints or task IDs. If the request
cannot be mapped to a supported operation, return GET /tasks with empty params.
"""


class VoiceProviderError(RuntimeError):
    pass


class InvalidInstructionError(ValueError):
    pass


def _validate_instruction(value: object) -> InstructionPayload:
    try:
        instruction = InstructionPayload.model_validate(value)
    except ValidationError as exc:
        raise InvalidInstructionError("Groq returned an invalid routing object.") from exc

    method = instruction.method.upper()
    task_id_route = re.fullmatch(r"/tasks/([1-9][0-9]*)", instruction.endpoint)
    supported = (
        (instruction.endpoint == "/tasks" and method in {"GET", "POST"})
        or (task_id_route is not None and method in {"PUT", "PATCH", "DELETE"})
    )
    if not supported:
        raise InvalidInstructionError("Groq returned an unsupported task route.")

    return InstructionPayload(
        endpoint=instruction.endpoint,
        method=method,
        params=instruction.params,
    )


async def generate_instruction(transcription: str) -> InstructionPayload:
    settings = get_settings()
    current_tasks = [task.model_dump() for task in task_routes.get_tasks()]
    user_content = json.dumps(
        {"transcription": transcription, "current_tasks": current_tasks},
        ensure_ascii=False,
    )

    try:
        base_url = settings.luna_url_base.rstrip("/")
        chat_url = (
            f"{base_url}/chat/completions"
            if base_url.endswith("/v1")
            else f"{base_url}/v1/chat/completions"
        )
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(
                chat_url,
                headers={"Authorization": f"Bearer {settings.luna_api_key}"},
                json={
                    "model": settings.luna_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0,
                },
            )
            response.raise_for_status()
            completion = response.json()
    except Exception as exc:
        logger.exception("LUNA instruction request failed (model=%s)", settings.luna_model)
        raise VoiceProviderError("LUNA could not generate an instruction.") from exc

    try:
        content = completion["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise InvalidInstructionError("LUNA returned an empty routing response.") from exc
    try:
        return _validate_instruction(json.loads(content or ""))
    except (json.JSONDecodeError, IndexError) as exc:
        raise InvalidInstructionError("LUNA did not return a valid JSON instruction.") from exc


async def transcribe_audio(
    filename: str,
    audio: bytes,
    content_type: str,
    language: str | None,
) -> str:
    settings = get_settings()

    try:
        async with AsyncGroq(
            api_key=settings.groq_api_key,
            timeout=settings.request_timeout_seconds,
        ) as client:
            transcription_options: dict[str, Any] = {
                "model": settings.groq_transcription_model,
                "file": (filename, audio, content_type),
                "response_format": "json",
            }
            if language is not None:
                transcription_options["language"] = language
            transcription = await client.audio.transcriptions.create(
                **transcription_options,
            )
    except Exception as exc:
        logger.exception(
            "Groq audio transcription failed (model=%s, filename=%s, content_type=%s, language=%s)",
            settings.groq_transcription_model,
            filename,
            content_type,
            language,
        )
        raise VoiceProviderError("Groq could not transcribe the audio.") from exc

    text = transcription.text.strip()
    if not text:
        raise InvalidInstructionError("No speech was detected in the audio.")
    return text


def execute_instruction(instruction: InstructionPayload) -> Any:
    task_id_match = re.fullmatch(r"/tasks/([1-9][0-9]*)", instruction.endpoint)
    task_id = int(task_id_match.group(1)) if task_id_match else None

    try:
        if instruction.endpoint == "/tasks" and instruction.method == "GET":
            return task_routes.get_tasks()
        if instruction.endpoint == "/tasks" and instruction.method == "POST":
            return task_routes.create_task(TaskCreate.model_validate(instruction.params))
        if task_id is not None and instruction.method == "PUT":
            return task_routes.replace_task(
                task_id,
                TaskReplace.model_validate(instruction.params),
            )
        if task_id is not None and instruction.method == "PATCH":
            return task_routes.update_task(
                task_id,
                TaskUpdate.model_validate(instruction.params),
            )
        if task_id is not None and instruction.method == "DELETE":
            return task_routes.delete_task(task_id)
    except ValidationError as exc:
        raise InvalidInstructionError("LUNA returned invalid task parameters.") from exc

    raise InvalidInstructionError("Groq returned an unsupported task operation.")