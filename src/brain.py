import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

SUMMARY_REQUEST = "can you summarize briefly this discussion for me? Answer in the language the messages were sent\n"

def get_generic_response(request) -> str:
    prompt = f"{HUMAN_PROMPT}" + request + f"{AI_PROMPT}"
    return use_brain(prompt)

def get_discussion_summary(discussion) -> str:
    prompt = f"{HUMAN_PROMPT}" + SUMMARY_REQUEST + discussion + f"{AI_PROMPT}"
    print(prompt)
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
