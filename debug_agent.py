# debug_agent.py
from dotenv import load_dotenv
load_dotenv(override=True)

from agent import create_agent

chat = create_agent()

print("Test 1:")
print(chat("hello"))
print()

print("Test 2:")
print(chat("I want to talk to receptionist"))