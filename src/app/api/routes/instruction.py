from fastapi import APIRouter, HTTPException, status

from src.app.schemas.voice import InstructionPayload, InstructionRequest
from src.app.services.voice import (
    InvalidInstructionError,
    VoiceProviderError,
    generate_instruction,
)

router = APIRouter(tags=["instruction"])


@router.post("/instruction", response_model=InstructionPayload)
async def route_instruction(
    payload: InstructionRequest,
) -> InstructionPayload:
    try:
        return await generate_instruction(payload.transcription)
    except InvalidInstructionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except VoiceProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
