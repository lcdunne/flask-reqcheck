from datetime import datetime


# Specific function to return error responses in JSON format
def handle_errors_with_json(error):
    return {
        "error": {
            "error": error.name,
            "detail": error.description,
            "code": error.code,
        },
        "timestamp": datetime.now(),
    }, error.code
