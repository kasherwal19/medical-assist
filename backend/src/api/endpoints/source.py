from fastapi import APIRouter, HTTPException
from lib.logger import logging
from models.source_models import SourceRequest, SourceResponse
from services.source_service import source_service

router = APIRouter()


@router.post("/view-sources", response_model=SourceResponse)
async def view_source_route(request: SourceRequest):
    try:
        logging.info(
            f"[view-sources] Request received | "
            f"session_id={request.session_id}, message_id={request.message_id}"
        )

        result = await source_service.process_source_request(request)

        # result is a dict
        if not result or result.get("count", 0) == 0:
            logging.warning(
                f"[view-sources] No images generated | "
                f"session_id={request.session_id}, message_id={result.get('message_id')}"
            )

        return result  # FastAPI will validate against SourceResponse

    except HTTPException:
        raise

    except Exception as exc:
        logging.error(
            f"[view-sources] Internal error | session_id={request.session_id}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate highlighted sources"
        )
