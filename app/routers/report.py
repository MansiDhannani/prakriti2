import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.models.schemas import NarrativeRequest, NarrativeResponse, PDFReportRequest, PDFResponse
from app.models.database import get_db
from app.services.db_service import save_report
from app.services.pdf_service import generate_pdf_b64

router = APIRouter()


@router.post("/report/narrative", response_model=NarrativeResponse)
def generate_narrative_endpoint(req: NarrativeRequest):
    """Generate an AI policy narrative using Claude. Requires GROQ_API_KEY."""
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY not configured. Set it in your .env file."
        )
    try:
        from app.services.narrative_service import generate_narrative
        return generate_narrative(
            valuation_result = req.valuation_result,
            scenario_results = req.scenario_results,
            location_name    = req.location_name,
            policy_context   = req.policy_context,
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report/pdf", response_model=PDFResponse)
def generate_pdf_endpoint(req: PDFReportRequest, db: Session = Depends(get_db)):
    """
    Generate a downloadable PDF policy report (returned as base64).
    Record is saved to the database automatically.
    """
    try:
        result = generate_pdf_b64(
            valuation_result = req.valuation_result,
            scenario_results = req.scenario_results,
            narrative        = req.narrative,
            location_name    = req.location_name,
            prepared_for     = req.prepared_for,
        )
        try:
            save_report(
                db,
                filename      = result["filename"],
                size_bytes    = result["size_bytes"],
                location_name = req.location_name,
                prepared_for  = req.prepared_for,
                has_narrative = bool(req.narrative),
                has_scenarios = bool(req.scenario_results),
            )
        except Exception as db_err:
            print(f"⚠ DB save failed (non-critical): {db_err}")
        return PDFResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report/pdf/download")
def download_pdf(req: PDFReportRequest, db: Session = Depends(get_db)):
    """Same as /report/pdf but returns raw PDF bytes for direct browser download."""
    try:
        import base64
        result = generate_pdf_b64(
            valuation_result = req.valuation_result,
            scenario_results = req.scenario_results,
            narrative        = req.narrative,
            location_name    = req.location_name,
            prepared_for     = req.prepared_for,
        )
        try:
            save_report(
                db,
                filename      = result["filename"],
                size_bytes    = result["size_bytes"],
                location_name = req.location_name,
                prepared_for  = req.prepared_for,
                has_narrative = bool(req.narrative),
                has_scenarios = bool(req.scenario_results),
            )
        except Exception as db_err:
            print(f"⚠ DB save failed (non-critical): {db_err}")

        pdf_bytes = base64.b64decode(result["pdf_base64"])
        return Response(
            content    = pdf_bytes,
            media_type = "application/pdf",
            headers    = {"Content-Disposition": f'attachment; filename="{result["filename"]}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
