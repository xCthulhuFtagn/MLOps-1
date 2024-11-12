import streamlit as st
import urllib.request
import urllib.parse
import pandas as pd
from PIL import Image
import json

API_URL = "http://localhost:8000/predict"

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im1heDEiLCJwYXNzd29yZCI6Im1heCJ9.11t5fsNHisVK79tCRVL8sSmCi3VnTtXGCI8WYBOECOA'

st.title("Interactive Prediction Dashboard")

uploaded_file = st.file_uploader("Upload a CSV file for prediction", type=["csv"])

def encode_multipart_formdata(fields, files):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = []
    for key, value in fields.items():
        body.append(f"--{boundary}")
        body.append(f'Content-Disposition: form-data; name="{key}"')
        body.append("")
        body.append(value)

    for key, file_info in files.items():
        filename, file_content, content_type = file_info
        body.append(f"--{boundary}")
        body.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"')
        body.append(f"Content-Type: {content_type}")
        body.append("")
        body.append(file_content)

    body.append(f"--{boundary}--")
    body.append("")
    body = "\r\n".join(body).encode("utf-8")
    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type

if uploaded_file is not None:
    input_data = pd.read_csv(uploaded_file)
    st.write("Data Preview:", input_data.head())

    model_class = st.selectbox("Select Model", ["GradientBoostingClassifier", "GradientBoostingRegressor"])

    if st.button("Predict"):
            try:
                fields = {"model_class": model_class}
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue().decode("utf-8"), "text/csv")
                }
                body, content_type = encode_multipart_formdata(fields, files)
                
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": content_type,
                    "accept": "application/json"
                }
                request = urllib.request.Request(API_URL, data=body, headers=headers)
                
                with urllib.request.urlopen(request) as response:
                    result = json.loads(response.read().decode())
                    predictions = result["0"]

                    prediction_df = pd.DataFrame(list(predictions.values()), columns=["Predicted Class"])
                    
                    st.subheader("Prediction Results")
                    st.write(prediction_df)

                    st.subheader("Prediction Visualization")
                    st.image(Image.open("./Imgs/fight.jpg"), caption="Результатов не будет, библиотеки для стримлита победили наш питон 3.13 в честном поединке за босса качалки")
                    
            except urllib.error.HTTPError as e:
                st.error(f"Prediction request failed: {e}")
                
