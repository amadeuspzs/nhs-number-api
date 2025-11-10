# 🤖 coded - here be dragons
import nhs_number

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

app = FastAPI(title="NHS Number API")


class ValidationResponse(BaseModel):
    valid: bool


class GenerateResponse(BaseModel):
    numbers: list[str]


class NormaliseResponse(BaseModel):
    normalised: str


@app.get("/")
def root():
    """Return a small swagger-like summary of available routes and options."""
    # region keys from the package mapping
    region_keys = sorted(list(nhs_number.REGIONS.keys()))

    # module-level REGION_* aliases exported by the package
    region_aliases = sorted(
        {
            name.removeprefix("REGION_")
            for name in dir(nhs_number)
            if name.startswith("REGION_")
        }
    )

    return {
        "title": app.title,
        "description": "A small machine-readable summary of available routes and their query/options.",
        "endpoints": [
            {
                "path": "/validate",
                "method": "GET",
                "query": {"number": "string (required)"},
                "description": "Validate an NHS number",
            },
            {
                "path": "/generate",
                "method": "GET",
                "query": {
                    "quantity": "int (1-100, default=1)",
                    "region": f"string (default=ENGLAND). Accepts keys {region_keys} or aliases {region_aliases}",
                },
                "description": "Generate one or more NHS numbers",
            },
            {
                "path": "/normalise",
                "method": "GET",
                "query": {"number": "string (required)"},
                "description": "Normalise/standardise an NHS number format",
            },
        ],
        "regions": {"keys": region_keys, "aliases": region_aliases},
    }


@app.get("/validate", response_model=ValidationResponse)
def validate(number: str = Query(..., description="NHS number to validate")):
    return {"valid": nhs_number.is_valid(number)}


@app.get("/generate", response_model=GenerateResponse)
def generate_numbers(
    quantity: int = Query(1, ge=1, le=100),
    region: str = Query(
        "ENGLAND", description="Region name: ENGLAND, WALES, ISLE_OF_MAN"
    ),
):
    # Accept region names like: ENGLAND, WALES, ISLE_OF_MAN, ENGLAND_WALES_IOM, SCOTLAND, NORTHERN_IRELAND, EIRE, etc.
    region_clean = region.upper().removeprefix("REGION_")

    # First try the REGIONS mapping exported by the nhs_number package
    region_obj = nhs_number.REGIONS.get(region_clean)

    # Fallback: the package also exposes module-level constants like REGION_ENGLAND, REGION_WALES, etc.
    if region_obj is None:
        region_attr = f"REGION_{region_clean}"
        region_obj = getattr(nhs_number, region_attr, None)

    if region_obj is None:
        raise HTTPException(status_code=400, detail=f"Invalid region: {region}")

    numbers = nhs_number.generate(quantity=quantity, for_region=region_obj)
    return {"numbers": numbers}


@app.get("/normalise", response_model=NormaliseResponse)
def normalise(number: str = Query(..., description="NHS number to normalise")):
    return {"normalised": nhs_number.normalise_number(number)}
