


import subprocess

LLAVA_EXEC_PATH = "~/Code/llama.cpp/build/bin/llava"
MODEL_PATH = "~/Models/ggml_llava-v1.5-7b/ggml-model-q5_k.gguf"
MMPROJ_PATH = "~/Models/ggml_llava-v1.5-7b/mmproj-model-f16.gguf"

PROMPT = "The image shows a site in Paris. Describe the image like a excited tourist guide. Give a short answer."

TEMP = 0.1 #  a lower temperature value like 0.1 is recommended for better quality.

def image_to_text(image_path, text_path):
    bash_command = f'{LLAVA_EXEC_PATH} -m {MODEL_PATH} --mmproj {MMPROJ_PATH} --temp {TEMP} -p "{PROMPT}"'

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
