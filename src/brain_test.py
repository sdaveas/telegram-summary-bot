from brain import get_generic_response, get_discussion_summary, get_answer_to_question, split_bill
import utils.logging as logging

logger = logging.GetLogger()

def test_get_generic_response() -> str:
    prompt = "Hello, how are you?"
    return get_generic_response(prompt)

def test_get_discussion_summary() -> str:
    discussion = "There's a new restaurant in town. I'm going to try it out. I'm excited!"
    return get_discussion_summary(discussion)

def test_get_answer_to_question() -> str:
    discussion = "I like to eat pizza, but I like burgers more"
    question = "What do I like more? Answer in one word"
    return get_answer_to_question(discussion, question)

def test_split_bill() -> str:
    photo_bytes = open("/Users/stelios/Downloads/receipt.jpg", "rb").read()
    description = "Alice: 1 chicken and 1 cola. Bob: 1 chicken. Charlie: 1 burger and a mac & cheese."
    return split_bill(photo_bytes, description)

def main():
    print("Testing split_bill")
    response = test_split_bill()
    print(response)
    print("--------------------------------")
    print("Testing get_generic_response")
    response = test_get_generic_response()
    print(response)
    print("--------------------------------")
    print("Testing get_discussion_summary")
    response = test_get_discussion_summary()
    print(response)
    print("--------------------------------")
    print("Testing get_answer_to_question")
    response = test_get_answer_to_question()
    print(response)
    print("--------------------------------")

if __name__ == "__main__":
    main()
