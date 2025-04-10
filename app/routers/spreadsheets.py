from fastapi import APIRouter, Depends, Path, Body
from app.dependencies.sheets import get_google_sheets_service
from app.dependencies.auth import get_current_user
from app.services.google_sheets import GoogleSheetsService
from app.models.base import CreateSheetRequest, RenameRequest
from app.utils import handle_exceptions

router = APIRouter(prefix="/api", tags=["spreadsheets"])


@router.post("/spreadsheets/create")
@handle_exceptions
def create_spreadsheet(
    request: CreateSheetRequest,
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    spreadsheet_id, url = service.create_spreadsheet(
        request.spreadsheet_name, request.sheet_title
    )

    return {"spreadsheet_id": spreadsheet_id, "url": url}


@router.put("/spreadsheets/{spreadsheet_id}/rename")
@handle_exceptions
def rename_spreadsheet(
    spreadsheet_id: str = Path(..., description="The ID of the Google Spreadsheet"),
    request: RenameRequest = Body(..., description="The new name for the spreadsheet"),
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    result = service.rename_spreadsheet(spreadsheet_id, request.new_name)
    return {"result": result}


@router.delete("/spreadsheets/{spreadsheet_id}")
@handle_exceptions
def delete_spreadsheet(
    spreadsheet_id: str = Path(..., description="The ID of the Google Spreadsheet"),
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    service.delete_spreadsheet(spreadsheet_id)
    return {"message": "Spreadsheet deleted successfully"}
