# import json

import cohere
from dotenv import find_dotenv, load_dotenv

from langtrace_python_sdk import langtrace

_ = load_dotenv(find_dotenv())

langtrace.init()

co = cohere.Client()


student_custom_functions = [
    {
        "name": "extract_student_info",
        "description": "Get the student information from the body of the input text",
        "parameter_definitions": {
            "name": {
                "type": "string",
                "description": "Name of the person",
                "required": True,
            },
            "major": {
                "type": "string",
                "description": "Major subject.",
                "required": True,
            },
            "school": {
                "type": "string",
                "description": "The university name.",
                "required": True,
            },
            "grades": {
                "type": "integer",
                "description": "GPA of the student.",
                "required": True,
            },
            "club": {
                "type": "string",
                "description": "School club for extracurricular activities. ",
                "required": False,
            },
        },
    }
]


def tool_calling():
    response = co.chat(
        message="John is a grad student in computer science at Stanford University. He is an American and has a 3.8 GPA. John is known for his programming skills and is an active member of the university's Robotics Club. He hopes to pursue a career in artificial intelligence after graduating.",
        tools=student_custom_functions,
    )
    print(response)
    return response
