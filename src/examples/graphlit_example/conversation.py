import asyncio
from dotenv import find_dotenv, load_dotenv
from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span
from openai import OpenAI
from graphlit import Graphlit
from graphlit_api import input_types, enums, exceptions

_ = load_dotenv(find_dotenv())

langtrace.init()


graphlit = Graphlit()

langtrace.init()
client = OpenAI()


async def complete():
    uri = "https://themixchief.com"
    try:
        ingest_response = await graphlit.client.ingest_uri(uri=uri, is_synchronous=True)
        content_id = ingest_response.ingest_uri.id if ingest_response.ingest_uri is not None else None

        if content_id is not None:
            print(f'Ingested content [{content_id}]:')

        prompt = "In 1 sentence, what does mixchief do."

        model = "gpt-4o"

        specification_input = input_types.SpecificationInput(
            name=f"OpenAI [{str(enums.OpenAIModels.GPT4O_128K)}]",
            type=enums.SpecificationTypes.COMPLETION,
            serviceType=enums.ModelServiceTypes.OPEN_AI,
            openAI=input_types.OpenAIModelPropertiesInput(
                model=enums.OpenAIModels.GPT4O_128K,
            )
        )

        specification_response = await graphlit.client.create_specification(specification_input)
        specification_id = specification_response.create_specification.id if specification_response.create_specification is not None else None

        if specification_id is not None:
            print(f'Created specification [{specification_id}].')

            conversation_input = input_types.ConversationInput(
                name="Conversation",
                specification=input_types.EntityReferenceInput(
                    id=specification_id
                ),
            )

            conversation_response = await graphlit.client.create_conversation(conversation_input)
            conversation_id = conversation_response.create_conversation.id if conversation_response.create_conversation is not None else None

            if conversation_id is not None:
                print(f'Created conversation [{conversation_id}].')

                format_response = await graphlit.client.format_conversation(prompt, conversation_id)
                formatted_message = format_response.format_conversation.message.message if format_response.format_conversation is not None and format_response.format_conversation.message is not None else None

                if formatted_message is not None:
                    stream_response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": formatted_message}],
                        temperature=0.1,
                        top_p=0.2,
                        stream=True
                    )

                    completion = ""

                    for chunk in stream_response:
                        delta = chunk.choices[0].delta.content

                        if delta is not None:
                            completion += delta

                    if completion is not None:
                        # NOTE: stores completion back into conversation
                        complete_response = await graphlit.client.complete_conversation(completion, conversation_id)

                        print(complete_response.complete_conversation.message.message if complete_response.complete_conversation is not None and complete_response.complete_conversation.message is not None else "None")
    except exceptions.GraphQLClientError as e:
        print(f"Graphlit API error: {e}")