from dotenv import load_dotenv
from embedchain import App
from langtrace_python_sdk import langtrace

load_dotenv()
langtrace.init()

app = App()
app.reset()
app.add("https://www.forbes.com/profile/elon-musk")
app.add("https://en.wikipedia.org/wiki/Elon_Musk")
res = app.query("What is the net worth of Elon Musk today?")
print(res)
re2 = app.search("Elon Musk")
print(re2)