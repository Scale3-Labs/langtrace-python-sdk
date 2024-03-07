import json

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

_ = load_dotenv(find_dotenv())

langtrace.init(batch=True, log_spans_to_console=True,
               write_to_remote_url=False)

client = OpenAI()


student_custom_functions = [
    {
        'name': 'extract_student_info',
        'description': 'Get the student information from the body of the input text',
        'parameters': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'Name of the person'
                },
                'major': {
                    'type': 'string',
                    'description': 'Major subject.'
                },
                'school': {
                    'type': 'string',
                    'description': 'The university name.'
                },
                'grades': {
                    'type': 'integer',
                    'description': 'GPA of the student.'
                },
                'club': {
                    'type': 'string',
                    'description': 'School club for extracurricular activities. '
                }

            }
        }
    }
]


@with_langtrace_root_span()
def function_calling():
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': "David Nguyen is a sophomore majoring in computer science at Stanford University. He is Asian American and has a 3.8 GPA. David is known for his programming skills and is an active member of the university's Robotics Club. He hopes to pursue a career in artificial intelligence after graduating."}],
        functions=student_custom_functions,
        function_call='auto',
        stream=False
    )

    # result = []
    # for chunk in response:
    #     if chunk.choices[0].delta.function_call is not None:
    #         content = [
    #             choice.delta.function_call.arguments if choice.delta.function_call and
    #             choice.delta.function_call.arguments else ""
    #             for choice in chunk.choices]
    #         result.append(
    #             content[0] if len(content) > 0 else "")

    # print("".join(result))

    # Loading the response as a JSON object
    json_response = json.loads(
        response.choices[0].message.function_call.arguments)
    print(json_response)
