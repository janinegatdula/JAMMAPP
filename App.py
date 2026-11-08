import streamlit as st

st.set_page_config(
    page_title="Star Explorer",
    page_icon="🌌",
    layout="wide"
)

st.title("🌌 Star Explorer")

st.write("Welcome to our Astronomy Data Exploration Platform!")

st.header("Explore the Universe")

st.markdown("""
This platform explores stellar properties,
supernova remnants, and possible stellar
evolutionary outcomes.
""")

if st.button("Start Exploring"):
    st.success("Welcome to Star Explorer!")