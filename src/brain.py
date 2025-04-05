import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import utils.logging as logging
import base64

logger = logging.GetLogger()

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

SUMMARY_REQUEST = "can you summarize briefly this discussion for me? Answer in the language the messages were sent\n"
QUESTION_REQUEST = "can you answer this question for me based on the discussion I will prove you?\n Here's the discussion: "
SPLIT_BILL_REQUEST = "can you split the bill for me based on the description and the photo? Any item that is not listed will be split equally. Add a 'Final totals' section at the very end to show the total amount each person owes. \n Here's the description: "
CONTEXT_PREFIX = "Here is some context about this chat that might be helpful:\n"

def create_text_messages(prompt: str) -> list[dict]:
    """Create a messages array for text-only queries."""
    return [{
        "role": "user",
        "content": prompt
    }]

def create_image_messages(image_bytes: bytes, text_prompt: str) -> list[dict]:
    """Create a messages array for queries that include an image."""
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    return [{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64_image
                }
            },
            {
                "type": "text",
                "text": text_prompt
            }
        ]
    }]

def use_brain(messages: list[dict], model: str = "claude-2", max_tokens: int = 600) -> str:
    """Make a direct call to anthropic.messages.create() with the provided messages array."""
    try:
        response = anthropic.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"Error generating AI response: {str(e)}"

def get_generic_response(request: str, context: str = "") -> str:
    prompt = f"{HUMAN_PROMPT}" + request + f"{CONTEXT_PREFIX}" + context + f"{AI_PROMPT}"
    logger.debug("prompt with discussion: [%s]", prompt)
    messages = create_text_messages(prompt)
    return use_brain(messages)

def get_discussion_summary(discussion: str, context: str = "") -> str:
    prompt = f"{HUMAN_PROMPT}" + SUMMARY_REQUEST + discussion + f"{CONTEXT_PREFIX}" + context + f"{AI_PROMPT}"
    logger.debug("prompt with discussion: [%s]", prompt)
    messages = create_text_messages(prompt)
    return use_brain(messages)

def get_answer_to_question(discussion: str, question: str, context: str = "") -> str:
    prompt = f"{HUMAN_PROMPT}" + QUESTION_REQUEST + discussion + "\n\nHere's the question: " + question + f"{CONTEXT_PREFIX}" + context + f"{AI_PROMPT}"
    logger.debug("prompt with discussion and question: [%s]", prompt)
    messages = create_text_messages(prompt)
    return use_brain(messages)

def split_bill(photo_bytes: bytes, description: str, context: str = "") -> str:
    try:
        text_prompt = f"{SPLIT_BILL_REQUEST}{description}" + f"{CONTEXT_PREFIX}" + context
        messages = create_image_messages(photo_bytes, text_prompt)
        return use_brain(messages, model="claude-3-5-sonnet-20240620", max_tokens=1000)
    except Exception as e:
        logger.error("Error processing bill: %s", str(e))
        return f"Error processing bill: {str(e)}"
