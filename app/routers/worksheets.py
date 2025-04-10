from fastapi import APIRouter, Path, Query, Body, Depends
from app.dependencies.sheets import get_google_sheets_service
from app.dependencies.auth import get_current_user
from app.services.google_sheets import GoogleSheetsService
from app.utils import handle_exceptions
from typing import List, Dict, Any

router = APIRouter(prefix="/api", tags=["worksheets"])


@router.get("/{spreadsheet_id}/worksheets")
@handle_exceptions
def get_worksheets(
    spreadsheet_id: str = Path(..., description="The ID of the Google Spreadsheet"),
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    names = service.get_worksheet_names(spreadsheet_id)
    return {"worksheets": names}


@router.get("/{spreadsheet_id}/{worksheet_name}")
@handle_exceptions
def get_worksheet_properties_by_name(
    spreadsheet_id: str = Path(..., description="The ID of the Google Spreadsheet"),
    worksheet_name: str = Path(..., description="The name of the worksheet"),
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    sheet_object = service.get_worksheet_by_name(spreadsheet_id, worksheet_name)
    return {"worksheet": sheet_object}


@router.put("/{spreadsheet_id}/{worksheet_name}/rename")
@handle_exceptions
def rename_worksheet(
    spreadsheet_id: str = Path(..., description="The ID of the Google Spreadsheet"),
    worksheet_name: str = Path(..., description="The name of the worksheet"),
    new_name: str = Query(..., description="The new name for the worksheet"),
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    result = service.rename_worksheet(spreadsheet_id, worksheet_name, new_name)
    return {"message": f"Worksheet renamed to {new_name}"}


@router.get("/{spreadsheet_id}/{worksheet_name}/read")
@handle_exceptions
def rename_worksheet(
    spreadsheet_id: str = Path(..., description="The ID of the Google Spreadsheet"),
    worksheet_name: str = Path(..., description="The name of the worksheet"),
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    data = service.read_worksheet(spreadsheet_id, worksheet_name)
    return data


@router.post("/{spreadsheet_id}/{worksheet_name}/write")
@handle_exceptions
def write_to_worksheet(
    spreadsheet_id: str = Path(..., description="The ID of the Google Spreadsheet"),
    worksheet_name: str = Path(..., description="The name of the worksheet"),
    data: List[Dict[str, Any]] = Body(
        ..., description="the data to write to the worksheet"
    ),
    start_cell: str = Query(
        "A1", description="The cell where teh data insertions should start"
    ),
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    service.write_to_worksheet(spreadsheet_id, worksheet_name, data, start_cell)
    return {"message": "Data written to the worksheet successfully"}


@router.post("/{spreadsheet_id}/{worksheet_name}/append")
@handle_exceptions
def append_records_to_worksheet(
    spreadsheet_id: str = Path(..., description="The ID of the Google Spreadsheet"),
    worksheet_name: str = Path(..., description="The name of the worksheet"),
    records: List[Dict[str, Any]] = Body(
        ..., description="The records to append to the worksheet"
    ),
    auto_increment_id: bool = Query(
        False, description="Whether to add an auto-incrementing 'id' column"
    ),
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    if auto_increment_id:
        service.append_records_autoincrement(spreadsheet_id, worksheet_name, records)
    else:
        service.append_records(spreadsheet_id, worksheet_name, records)

    return {"message": "Records appended to the worksheet successfully"}


@router.post("/{spreadsheet_id}/{worksheet_name}/add")
@handle_exceptions
def add_a_new_worksheet(
    spreadsheet_id: str = Path(..., description="The ID of the Google Spreadsheet"),
    worksheet_name: str = Path(..., description="The name of the worksheet"),
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    result = service.add_worksheet(spreadsheet_id, worksheet_name)
    return {"result": result}


@router.put("/{spreadsheet_id}/{worksheet_name}/clear")
@handle_exceptions
def clear_all_the_content_of_a_worksheet(
    spreadsheet_id: str = Path(..., description="The ID of the Google Spreadsheet"),
    worksheet_name: str = Path(..., description="The name of the worksheet"),
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    result = service.clear_worksheet(spreadsheet_id, worksheet_name)
    return {"result": result}


@router.delete("/{spreadsheet_id}/{worksheet_name}/delete")
@handle_exceptions
def delete_a_worksheet(
    spreadsheet_id: str = Path(..., description="The ID of the Google Spreadsheet"),
    worksheet_name: str = Path(..., description="The name of the worksheet"),
    current_user=Depends(get_current_user),
    service: GoogleSheetsService = Depends(get_google_sheets_service),
):
    result = service.delete_worksheet(spreadsheet_id, worksheet_name)
    return {"result": result}
