from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import HTTPException
from typing import List, Dict, Any


class GoogleSheetsService:
    def __init__(self, creds):
        self.sheets_service = build("sheets", "v4", credentials=creds).spreadsheets()
        self.drive_service = build("drive", "v3", credentials=creds)

    def create_spreadsheet(self, spreadsheet_name: str, sheet_title: str):
        body = {
            "properties": {"title": spreadsheet_name},
            "sheets": [{"properties": {"title": sheet_title}}],
        }

        response = self.sheets_service.create(body=body).execute()

        spreadsheet_id = response["spreadsheetId"]
        share_link = response["spreadsheetUrl"]

        permission = {
            "role": "writer",
            "type": "user",
            "emailAddress": "tcwicklund@gmail.com",
        }

        # permission = {
        #     "role": "writer",
        #     "type": "anyone"
        # }

        self.drive_service.permissions().create(
            fileId=spreadsheet_id, body=permission
        ).execute()

        return spreadsheet_id, share_link

    def rename_spreadsheet(self, spreadsheet_id: str, new_name: str):
        request_body = {
            "requests": [
                {
                    "updateSpreadsheetProperties": {
                        "properties": {"title": new_name},
                        "fields": "title",
                    }
                }
            ]
        }

        result = self.sheets_service.batchUpdate(
            spreadsheetId=spreadsheet_id, body=request_body
        ).execute()

        return result

    def delete_spreadsheet(self, spreadsheet_id: str):
        self.drive_service.files().delete(fileId=spreadsheet_id).execute()

    def get_worksheet_names(self, spreadsheet_id: str) -> List[str]:
        metadata = self.sheets_service.get(spreadsheetId=spreadsheet_id).execute()
        worksheets = metadata.get("sheets", [])
        worksheet_names = [sheet["properties"]["title"] for sheet in worksheets]
        return worksheet_names

    def get_worksheet_by_name(self, spreadsheet_id: str, worksheet_name: str):
        metadata = self.sheets_service.get(spreadsheetId=spreadsheet_id).execute()
        worksheets = metadata.get("sheets", [])
        worksheet = next(
            (
                sheet
                for sheet in worksheets
                if sheet["properties"]["title"] == worksheet_name
            ),
            None,
        )

        if worksheet is None:
            raise HTTPException(
                status_code=404, detail=f"Worksheet '{worksheet_name}' was not found"
            )

        return worksheet

    def rename_worksheet(self, spreadsheet_id: str, worksheet_name: str, new_name: str):
        worksheet = self.get_worksheet_by_name(spreadsheet_id, worksheet_name)
        sheet_id = worksheet["properties"]["sheetId"]

        request_body = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": sheet_id, "title": new_name},
                        "fields": "title",
                    }
                }
            ]
        }

        result = self.sheets_service.batchUpdate(
            spreadsheetId=spreadsheet_id, body=request_body
        ).execute()

        return result

    def read_worksheet(self, spreadsheet_id: str, worksheet_name: str):
        range_name = f"{worksheet_name}!A1:ZZZ"

        result = (
            self.sheets_service.values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )

        rows = result.get("values", [])

        if not rows:
            return []

        column_names = rows[0]
        data = [dict(zip(column_names, row)) for row in rows[1:]]

        return data

    def write_to_worksheet(
        self,
        spreadsheet_id: str,
        worksheet_name: str,
        data: List[Dict[str, Any]],
        start_cell: str = "A1",
    ):

        # headers = list(set(key for row in data for key in row.keys()))
        # { a b c } -> { b c a}

        headers = []
        for row in data:
            for key in row.keys():
                if key not in headers:
                    headers.append(key)

        values = [headers]

        for row in data:
            row_values = []

            for header in headers:
                row_values.append(row.get(header, ""))

            values.append(row_values)

        range_name = f"{worksheet_name}!{start_cell}"

        body = {"values": values}

        self.sheets_service.values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def append_records(
        self,
        spreadsheet_id: str,
        worksheet_name: str,
        records: List[Dict[str, Any]],
    ):
        existing_data = self.read_worksheet(spreadsheet_id, worksheet_name)

        existing_headers = []
        for row in existing_data:
            for header in row.keys():
                if header not in existing_headers:
                    existing_headers.append(header)

        new_headers = set()
        new_records = []

        for record in records:
            row_values = [str(record.get(header, "")) for header in existing_headers]
            record_new_headers = [
                key for key in record.keys() if key not in existing_headers
            ]
            new_headers.update(record_new_headers)

        if new_headers:
            all_headers = existing_headers + list(new_headers)

            headers_range = f"{worksheet_name}!{chr(ord('A') + len(existing_headers))}1:{chr(ord('A') + len(all_headers)-1)}1"

            headers_body = {"values": [list(new_headers)]}

            self.sheets_service.values().update(
                spreadsheetId=spreadsheet_id,
                range=headers_range,
                valueInputOption="USER_ENTERED",
                body=headers_body,
            ).execute()
        else:
            all_headers = existing_headers

        for record in records:
            row_values = [str(record.get(header, "")) for header in all_headers]
            new_records.append(row_values)

        start_row = len(existing_data) + 1
        range_name = f"{worksheet_name}!A{start_row}"

        body = {"values": new_records}

        self.sheets_service.values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()

    def append_records_autoincrement(
        self,
        spreadsheet_id: str,
        worksheet_name: str,
        records: List[Dict[str, Any]],
    ):
        existing_data = self.read_worksheet(spreadsheet_id, worksheet_name)

        max_id = 0
        for row in existing_data:
            if "id" in row and str(row["id"]).isdigit():
                max_id = max(max_id, int(row["id"]))

        for i, record in enumerate(records, start=max_id + 1):
            record["id"] = str(i)

        self.append_records(spreadsheet_id, worksheet_name, records)

    def add_worksheet(self, spreadsheet_id: str, worksheet_name: str):
        request_body = {
            "requests": [{"addSheet": {"properties": {"title": worksheet_name}}}]
        }

        result = self.sheets_service.batchUpdate(
            spreadsheetId=spreadsheet_id, body=request_body
        ).execute()

        return result

    def clear_worksheet(self, spreadsheet_id: str, worksheet_name: str):
        result = (
            self.sheets_service.values()
            .clear(spreadsheetId=spreadsheet_id, range=f"{worksheet_name}!A:ZZZ")
            .execute()
        )

        return result

    def delete_worksheet(self, spreadsheet_id: str, worksheet_name: str):
        worksheet = self.get_worksheet_by_name(spreadsheet_id, worksheet_name)
        sheet_id = worksheet["properties"]["sheetId"]

        request_body = {"requests": [{"deleteSheet": {"sheetId": sheet_id}}]}

        result = self.sheets_service.batchUpdate(
            spreadsheetId=spreadsheet_id, body=request_body
        ).execute()

        return result
