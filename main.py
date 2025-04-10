from fastapi import FastAPI
from app.routers.spreadsheets import router as spreadsheets_router
from app.routers.worksheets import router as worksheets_router
from app.routers.authentication import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Python Google Sheets API",
    description="A python API to interact with Google Sheets",
    version="1.0",
    docs_url="/",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Authenticate clients to access the API",
        },
        {
            "name": "spreadsheets",
            "description": "Operations on spreadsheets",
        },
        {
            "name": "worksheets",
            "description": "Operations on worksheets within a given spreadsheet",
        },
    ],
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spreadsheets_router)
app.include_router(worksheets_router)
app.include_router(auth_router)
