from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError
from starlette.datastructures import UploadFile

from src.app.schemas.voice import InstructionRequest, TranscribeFlowResponse
from src.app.services.voice import (
    InvalidInstructionError,
    VoiceProviderError,
    execute_instruction,
    generate_instruction,
    transcribe_audio,
)
from src.app.utils.language import normalize_transcription_language

router = APIRouter(tags=["transcribe"])


@router.get("/")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/transcribe", response_model=TranscribeFlowResponse)
async def transcribe_and_run_flow(request: Request) -> TranscribeFlowResponse:
    content_type = request.headers.get("content-type", "")

    try:
        if content_type.startswith("multipart/form-data"):
            form = await request.form()
            try:
                uploaded_file = form.get("file")
                if not isinstance(uploaded_file, UploadFile):
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Multipart field 'file' is required.",
                    )

                audio = await uploaded_file.read()
                if not audio:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Uploaded audio is empty.",
                    )

                language = normalize_transcription_language(form.get("language"))
                filename = uploaded_file.filename or "recording.webm"
                audio_content_type = uploaded_file.content_type or "application/octet-stream"
            finally:
                await form.close()

            transcription = await transcribe_audio(
                filename=filename,
                audio=audio,
                content_type=audio_content_type,
                language=language,
            )
        elif content_type.startswith("application/json"):
            try:
                payload = InstructionRequest.model_validate(await request.json())
            except (ValidationError, ValueError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="A non-empty 'transcription' field is required.",
                ) from exc
            transcription = payload.transcription
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Send multipart audio or a JSON transcription.",
            )

        instruction = await generate_instruction(transcription)
        result = execute_instruction(instruction)
        return TranscribeFlowResponse(
            transcription=transcription,
            instruction=instruction,
            result=result,
        )
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
