import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import utils.logging as logging
import base64

logger = logging.GetLogger()

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

SUMMARY_REQUEST = "can you summarize briefly this discussion for me? Answer in the language the messages were sent\n"
QUESTION_REQUEST = "can you answer this question for me based on the discussion I will prove you? Answer in the language the messages were sent\n Here's the discussion: "
SPLIT_BILL_REQUEST = "can you split the bill for me based on the description and the photo? Any item that is not listed will be split equally. Add a 'Final totals' section at the very end to show the total amount each person owes. \n Here's the photo and the description: "

def get_generic_response(request) -> str:
    prompt = f"{HUMAN_PROMPT}" + request + f"{AI_PROMPT}"
    logger.debug("prompt with discussion: [%s]", prompt)

    return use_brain(prompt)

def get_discussion_summary(discussion) -> str:
    prompt = f"{HUMAN_PROMPT}" + SUMMARY_REQUEST + discussion + f"{AI_PROMPT}"
    logger.debug("prompt with discussion: [%s]", prompt)

    return use_brain(prompt)

def get_answer_to_question(discussion, question) -> str:
    prompt = f"{HUMAN_PROMPT}" + QUESTION_REQUEST + discussion + "\n\nHere's the question: " + question + f"{AI_PROMPT}"
    logger.debug("prompt with discussion and question: [%s]", prompt)

    return use_brain(prompt)

def use_brain(prompt) -> str:
    try:
        response = anthropic.completions.create(
            model="claude-2",
            prompt=prompt,
            max_tokens_to_sample=600,
        )
        return response.completion
    except Exception as e:
        return f"Error generating AI summary: {str(e)}"

def split_bill(photo_bytes: str, description: str) -> str:
    try:
        base64_image = base64.b64encode(photo_bytes).decode('utf-8')

        response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            messages=[
                {
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
                            "text": f"{SPLIT_BILL_REQUEST}\n\nDescription: {description}"
                        }
                    ]
                }
            ]
        )

        return response.content[0].text
    except Exception as e:
        logger.error("Error processing bill: %s", str(e))
        return f"Error processing bill: {str(e)}"
