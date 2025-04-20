# app/routes/project_parser.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Path
from xknxproject import XKNXProj
from xknxproject.models import KNXProject
import os
import json
from urllib.parse import unquote

router = APIRouter()

UPLOAD_DIR = "./app/uploads"
PARSED_OUTPUT = os.path.join(UPLOAD_DIR, "parsed_knx_project.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post(
    "/import-knx-project",
    tags=["Project Import"],
    summary="Import and parse KNX project",
    description="Uploads an ETS project file (.knxproj), parses it, and saves the parsed data as JSON."
)
async def import_knx_project(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".knxproj"):
            raise HTTPException(status_code=400, detail="Invalid file type")

        filepath = os.path.join(UPLOAD_DIR, file.filename)

        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)

        try:
            knxproj: XKNXProj = XKNXProj(path=filepath)
            parsed: KNXProject = knxproj.parse()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to parse KNX project: {e}"
            )

        with open(PARSED_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)

        return {"status": "✅ KNX project parsed successfully", "file": file.filename}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/knx-project",
    tags=["Project Import"],
    summary="Get parsed KNX project summary",
    description="Returns a summary of the parsed KNX project, including info, locations, group addresses, and functions."
)
async def get_knx_project():
    try:
        if not os.path.exists(PARSED_OUTPUT):
            raise HTTPException(status_code=404, detail="No parsed project found")

        with open(PARSED_OUTPUT, "r", encoding="utf-8") as f:
            full_data = json.load(f)
            summary = {
                "info": full_data.get("info", {}),
                "locations": full_data.get("locations", {}),
                "group_addresses": full_data.get("group_addresses", {}),
                "functions": full_data.get("functions", {}),
            }
            return summary
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/topology",
    tags=["Project Structure"],
    summary="Get topology hierarchy",
    description="Returns the topology hierarchy of the parsed KNX project."
)
def get_topology_hierarchy():
    try:
        if not os.path.exists(PARSED_OUTPUT):
            raise HTTPException(status_code=404, detail="No parsed project found")

        with open(PARSED_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)
            topology = data.get("topology", {})
            return topology
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/devices-lite",
    tags=["Devices"],
    summary="Get lite list of devices",
    description="Returns a simplified list of devices without communication object IDs and channels."
)
def get_lite_list_of_devices():
    try:
        if not os.path.exists(PARSED_OUTPUT):
            raise HTTPException(status_code=404, detail="No parsed project found")

        with open(PARSED_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)
            devices = data.get("devices", {})

            def strip_communication_object_ids(obj):
                if isinstance(obj, dict):
                    obj.pop("communication_object_ids", None)
                    obj.pop("channels", None)
                    for key in obj:
                        strip_communication_object_ids(obj[key])
                elif isinstance(obj, list):
                    for item in obj:
                        strip_communication_object_ids(item)

            strip_communication_object_ids(devices)
            return devices
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/devices-full",
    tags=["Devices"],
    summary="Get full list of devices",
    description="Returns the full list of devices parsed from the KNX project."
)
def get_full_list_of_devices():
    try:
        if not os.path.exists(PARSED_OUTPUT):
            raise HTTPException(status_code=404, detail="No parsed project found")

        with open(PARSED_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)
            devices = data.get("devices", {})
            return devices
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/device/{individual_address}",
    tags=["Devices"],
    summary="Get device by individual address",
    description="Returns a specific device by its individual address."
)
async def get_device_by_individual_address(individual_address: str):
    try:
        if not os.path.exists(PARSED_OUTPUT):
            raise HTTPException(status_code=404, detail="No parsed project found")

        with open(PARSED_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)
            devices = data.get("devices", {})

            device = devices.get(individual_address)
            if device:
                return device
            else:
                raise HTTPException(status_code=404, detail="Device not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/locations",
    tags=["Project Structure"],
    summary="Get locations hierarchy",
    description="Returns the hierarchy of locations in the KNX project, excluding devices and functions."
)
def get_locations_hierarchy():
    try:
        if not os.path.exists(PARSED_OUTPUT):
            raise HTTPException(status_code=404, detail="No parsed project found")

        with open(PARSED_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)
            locations = data.get("locations", {})

            def strip_devices_and_functions(obj):
                if isinstance(obj, dict):
                    obj.pop("devices", None)
                    obj.pop("functions", None)
                    for key in obj:
                        strip_devices_and_functions(obj[key])
                elif isinstance(obj, list):
                    for item in obj:
                        strip_devices_and_functions(item)

            strip_devices_and_functions(locations)
            return locations
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


from fastapi import APIRouter, HTTPException
import os
import json

router = APIRouter()

PARSED_OUTPUT = "uploads/parsed_knx_project.json"

@router.get(
    "/location/{name}",
    tags=["Project Structure"],
    summary="Get location by name",
    description="Returns a specific location by its name."
)
async def get_location_by_name(name: str):
    try:
        if not os.path.exists(PARSED_OUTPUT):
            raise HTTPException(status_code=404, detail="No parsed project found")

        with open(PARSED_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)
            locations = data.get("locations", {})

            def find_location_by_name(obj, name):
                if isinstance(obj, dict):
                    if obj.get("name") == name:
                        return obj
                    for key in obj:
                        result = find_location_by_name(obj[key], name)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = find_location_by_name(item, name)
                        if result:
                            return result
                return None

            location = find_location_by_name(locations, name)
            if location:
                return location
            else:
                raise HTTPException(status_code=404, detail="Location not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )



@router.get(
    "/functions",
    tags=["Functions"],
    summary="Get all functions",
    description="Returns all functions parsed from the KNX project."
)
async def get_functions():
    try:
        if not os.path.exists(PARSED_OUTPUT):
            raise HTTPException(status_code=404, detail="No parsed project found")

        with open(PARSED_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)
            functions = data.get("functions", {})
            return functions
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/function/{identifier}",
    tags=["Functions"],
    summary="Get function by identifier",
    description="Returns a specific function by its identifier."
)
async def get_function_by_identifier(identifier: str):
    try:
        if not os.path.exists(PARSED_OUTPUT):
            raise HTTPException(status_code=404, detail="No parsed project found")

        with open(PARSED_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)
            functions = data.get("functions", {})

            function = functions.get(identifier)
            if function:
                return function
            else:
                raise HTTPException(status_code=404, detail="Function not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/group-addresses",
    tags=["Group Addresses"],
    summary="List all group addresses",
    description="Returns all group addresses parsed from the uploaded KNX project."
)
async def get_group_addresses():
    try:
        if not os.path.exists(PARSED_OUTPUT):
            raise HTTPException(status_code=404, detail="No parsed project found")

        with open(PARSED_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)
            group_addresses = data.get("group_addresses", {})
            return group_addresses
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/group-address/{address:path}",
    tags=["Group Addresses"],
    summary="Get group address by address",
    description="Returns a specific group address by its address (e.g., 0/0/4)."
)
async def get_group_address_by_address(address: str = Path(...)):
    try:
        if not os.path.exists(PARSED_OUTPUT):
            raise HTTPException(status_code=404, detail="No parsed project found")

        decoded_address = unquote(address)

        with open(PARSED_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)
            group_addresses = data.get("group_addresses", {})

            group_address = group_addresses.get(decoded_address)
            if group_address:
                return group_address
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Group address '{decoded_address}' not found",
                )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )
