from langtrace.trace_attributes import LangTraceSpanAttributes
from langtrace.trace_attributes import OpenAISpanAttributes
from langtrace.trace_attributes import Event

# Instantiate the model
attributes = LangTraceSpanAttributes.model_validate({'service.provider': 'OpenAI'})

# Print the model as a JSON string
print(attributes.model_dump_json(by_alias=True))
