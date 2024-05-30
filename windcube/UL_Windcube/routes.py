from fastapi import APIRouter, status

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from UL_Windcube.service import CsvFilesProcess

router = APIRouter()

# --------------------------------------
#   Get UL_Windcube data by filter parameters
# ------------------------------------
@router.get("/")
async def get_windcube_data_by_filter(year: str, month: str, refresh: bool):
    """
    This API provides all the information neede for generating graph data and table data
    """

    process_csv_files_obj = CsvFilesProcess(year, month, refresh)
    await process_csv_files_obj.process_files()
    data = await process_csv_files_obj.process_master_file()
    json_compatible_list = jsonable_encoder(data)
    return JSONResponse(content=json_compatible_list, status_code=status.HTTP_200_OK)
