from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

# from PIL import Image


_ = load_dotenv(find_dotenv())

langtrace.init(write_spans_to_console=True)


client = OpenAI()


# use this to convert the image to RGBA
# def convert_to_rgba():
#     Image.open("./resources/ip1.png").convert("RGBA").save("./resources/ip1a.png")


def image_edit():

    response = client.images.edit(
        model="dall-e-2",
        image=open("./resources/lounge_flamingo.png", "rb"),
        mask=open("./resources/mask.png", "rb"),
        prompt="A sunlit indoor lounge area with a pool and duck standing in side with flamingo.",
        n=1,
        size="1024x1024",
        response_format="url",
    )

    image_url = response.data[0].url
    print(image_url)
    print(response)


image_edit()
# convert_to_rgba()
