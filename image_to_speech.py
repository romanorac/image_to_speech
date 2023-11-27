# Install the packages by running this in terminal
# pip install -U streamlit==1.28.2 pyobjc==9.0.1 pyttsx3==2.90

import pathlib
import subprocess
import streamlit as st
import tempfile
import pyttsx3
from enum import Enum
from dataclasses import dataclass

# path configuration
LLAVA_EXEC_PATH = "~/Code/llama.cpp/build/bin/llava"
MODEL_PATH = "~/Models/ggml_llava-v1.5-7b/ggml-model-q5_k.gguf"
MMPROJ_PATH = "~/Models/ggml_llava-v1.5-7b/mmproj-model-f16.gguf"

TEMP = 0.1 #  a lower temperature value like 0.1 is recommended for better quality.


# Agents definition
class AgentEnum(Enum):
    PARIS_TOURIST_GUIDE = "Paris Tourist Guide"
    SIGHTED_GUIDE = "Sighted Guide"
    SOCCER_COMMENTARY = "Soccer Commentary"


# python class that stores information about the agent
@dataclass
class Agent:
    name: str # name is shown in the web app ratio button
    prompt: str # prompt that is sent to the model
    voice_id: int # you can play with different voices


# Define 3 agents
AGENT_DICT = {
    AgentEnum.PARIS_TOURIST_GUIDE.value: Agent(
        name=AgentEnum.PARIS_TOURIST_GUIDE.value,
        prompt="""
        The image shows a site in Paris. Describe the image like a excited tourist guide. Give a short answer.
        """,
        voice_id=-1,  # use default voide
    ),
    AgentEnum.SIGHTED_GUIDE.value: Agent(
        name=AgentEnum.SIGHTED_GUIDE.value,
        prompt="""You are sighted guide for a visually impaired individual. 
                  Concisely describe any potential dangers or hazards present in the image. 
                  """,
        voice_id=-1,  # use default voide
    ),
    AgentEnum.SOCCER_COMMENTARY.value: Agent(
        name=AgentEnum.SOCCER_COMMENTARY.value,
        prompt="""You are commentating on a soccer match.
                  Respond with one or two excited statements.
                  """,
        voice_id=-1,  # use default voide
    ),
}

# generate text from an image
def image_to_text(image_path, text_path, agent):
    bash_command = f'{LLAVA_EXEC_PATH} -m {MODEL_PATH} --mmproj {MMPROJ_PATH} --temp {TEMP} -p "{agent.prompt}"'

    bash_command_cur = f'{bash_command} --image "{image_path}" > "{text_path}"'

    process = subprocess.Popen(
        bash_command_cur, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    output, error = process.communicate()

    print("Output:")
    print(output.decode("utf-8"))

    print("Error:")
    print(error.decode("utf-8"))

    return_code = process.returncode
    return return_code == 0

# extract only the the model response and skip the model logs
def clean_text(image_text):
    image_text_split = image_text.split("\n")

    end_index_list = [
        i for i, line in enumerate(image_text_split) if line.startswith("main:")
    ]
    if len(end_index_list) == 1 and (end_index_list[0] - 2) >= 0:
        end_index = end_index_list[0]
        image_text_cleaned = "".join(image_text_split[end_index - 2]).strip()
        return image_text_cleaned
    return "Text could not be cleaned"


# this function is used to beautify the generated text on the web page
# by showing each statement in a new line
def split_text_by_dot(image_text):
    return ".\n".join(t.strip() for t in image_text.split("."))


# generate speech from text
def text_to_speech(text, agent):
    engine = pyttsx3.init()
    rate = engine.getProperty("rate")
    engine.setProperty("rate", rate - 20)

    voices = engine.getProperty("voices")
    if agent.voice_id >= 0 and agent.voice_id < len(voices):
        engine.setProperty("voice", voices[agent.voice_id].id)

    engine.say(text)
    engine.runAndWait()


def main():
    st.title("📸 Image to Speech🎶")

    # show all agents in the ratio button
    agent_radio = st.sidebar.radio(
        "Prompt", (agent_enum.value for agent_enum in AgentEnum)
    )
    print(agent_radio)

    # extract an agent
    agent = AGENT_DICT[agent_radio]

    # upload image placeholder
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "png"])

    if uploaded_file is None:
        return

    # # show image on the web page
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()

    st.subheader("Image")
    st.image(bytes_data, width=500)

    # prepare paths for text and image in the temp folder
    image_path = pathlib.Path(tempfile.gettempdir(), uploaded_file.name)
    text_path = image_path.with_suffix(".txt")
    print("image_path", image_path)
    print("text path", text_path)

    # save the image into temp folder
    with open(str(image_path), "wb") as f:
        f.write(uploaded_file.getbuffer())

    # generate the text from an image
    success = image_to_text(image_path, text_path, agent)
    if not success:
        st.text("There was a problem with text extraction from an image. Check logs")
        return

    # read the generated text
    text = text_path.read_text()
    if not text or len(text) == 0:
        st.text("No text was read")
        return

    text = clean_text(text)
    st.subheader(f"Text generated by {agent.name}")
    st.text(split_text_by_dot(text))
    text_to_speech(text, agent)


if __name__ == "__main__":
    main()
