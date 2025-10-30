import json
import streamlit as st
from dotenv import load_dotenv
import os
import boto3

# Load environment variables
load_dotenv()

USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

cognito_client = boto3.client(
    "cognito-idp",
    region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def get_user_email(user_id: str) -> str:
    try:
        response = cognito_client.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=user_id
        )
        for attr in response.get("UserAttributes", []):
            if attr["Name"] == "email":
                return attr["Value"]
    except Exception as e:
        return f"Unknown ({user_id[:6]}...)"
    return "Unknown"


# Streamlit UI
st.title("Conversation Viewer")

uploaded_file = st.file_uploader("Upload a conversation JSON file", type=["json"])

if uploaded_file is not None:
    data = json.load(uploaded_file)

    for message in data:
        role = message.get("role")
        content = message.get("content", "")
        timestamp = message.get("timestamp", "")

        if role == "user":
            user_id = message["metadata"]["User ID"]
            email = get_user_email(user_id)
            tag = email
            bubble_type = "user"
        else:
            tag = "Assistant"
            bubble_type = "assistant"

        with st.chat_message(bubble_type):
            st.markdown(f"**{tag}** ({timestamp})")
            st.write(content)
