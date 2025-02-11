import streamlit as st


page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://i.brecorder.com/primary/2021/03/604bec2467e36.jpg");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
st.title("Streamlit App with Background Image")


