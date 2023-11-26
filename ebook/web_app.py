# import required packages
import pathlib
import streamlit as st
import tempfile

def main():
    # show the title of the web application
    st.title("📸 Image to Speech 🎶")

    # create a placeholder to upload the image
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "png"])

    # stop if there is no uploaded file
    if uploaded_file is None:
        return

    # Read file as bytes so that it can be shown on the page
    bytes_data = uploaded_file.getvalue()

    st.subheader("Image")

    # Show the image on the web page
    st.image(bytes_data, width=500)

    # Define the input and output paths for the image and text in temp dir
    image_path = pathlib.Path(tempfile.gettempdir(), uploaded_file.name)
    text_path = image_path.with_suffix(".txt")

    # Save image to temp dir
    with open(str(image_path), "wb") as f:
        f.write(uploaded_file.getbuffer())

    # generate text from an image
    success = image_to_text(image_path, text_path, agent)
    if not success:
        st.text("There was a problem with text extraction from an image. Check logs")
        return

    # wrap to the code above in text_to_speech function
    text_to_speech(text)







