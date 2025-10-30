import boto3
import json
import os
import streamlit as st
from dotenv import load_dotenv
import os



# load .env file
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
    """Given a user_id (sub), fetch the email attribute from AWS Cognito
    Args:
        user_id: string representing the user
    Returns:
        str of the user email
    """
    try:
        response = cognito_client.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=user_id
        )
        for attr in response.get("UserAttributes", []):
            if attr["Name"] == "email":
                return attr["Value"]
    except Exception as e:
        print(f"Error fetching email for {user_id}: {e}")
    return f"Unknown ({user_id[:6]}...)"


def load_conversation(file_path: str):
    """ Load the JSON conversation from file.
    Args:
        file_path: the string path to JSON file
    Returns:
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def visualize_conversation(conversation):
    """ Renders the conversation using Streamlit.
    """
    st.title("Conversation Viewer")

    for message in conversation:
        role = message.get("role")
        content = message.get("content", "")
        timestamp = message.get("timestamp", "")

        # If user, replace ID with email
        if role == "user":
            user_id = message["metadata"]["User ID"]
            email = get_user_email(user_id)
            tag = email
            is_user = True
        else:
            tag = "Assistant"
            is_user = False

        with st.chat_message("user" if is_user else "assistant"):
            st.markdown(f"**{tag}** ({timestamp})")
            st.write(content)


if __name__ == "__main__":
    # read json file path
    conversation = load_conversation("chat_history.json")
    visualize_conversation(conversation)
