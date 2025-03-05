import os

from cleanlab_tlm import TLM
from dotenv import find_dotenv, load_dotenv

from langtrace_python_sdk import langtrace

_ = load_dotenv(find_dotenv())

langtrace.init()

api_key = os.getenv("CLEANLAB_API_KEY")
tlm = TLM(api_key=api_key, options={"log": ["explanation"], "model": "gpt-4o-mini"}) # GPT, Claude, etc
out = tlm.prompt("What's the third month of the year alphabetically?")
trustworthiness_score = tlm.get_trustworthiness_score("What's the first month of the year?", response="January")

print(out)
print(trustworthiness_score)
