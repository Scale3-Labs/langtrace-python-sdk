from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from langtrace_python_sdk import langtrace, with_langtrace_root_span, SendUserFeedback

_ = load_dotenv(find_dotenv())

# Initialize Langtrace SDK
langtrace.init()
client = OpenAI()


def api(span_id, trace_id):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "What is the best place to live in the US?"},
        ],
        stream=False,
    )

    # Collect user feedback and send it to Langtrace
    user_score = 1  # Example user score
    user_id = 'user_1234'  # Example user ID
    data = {
        "userScore": user_score,
        "userId": user_id,
        "spanId": span_id,
        "traceId": trace_id
    }
    SendUserFeedback().evaluate(data=data)

    # Return the response
    return response.choices[0].message.content


# wrap the API call with the Langtrace root span
wrapped_api = with_langtrace_root_span()(api)

# Call the wrapped API
wrapped_api()
