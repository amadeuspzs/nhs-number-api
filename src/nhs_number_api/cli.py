import uvicorn


def main():
    uvicorn.run("nhs_number_api.main:app", host="0.0.0.0", port=8000, reload=True)
