# test_agent.py

from agent import create_agent

print("Starting Paw Connect AI Agent...")
print("=" * 50)

chat = create_agent()
print("Agent created successfully!")
print("=" * 50)

print("\nTEST 1 - FAQ Question:")
print("Customer: What are your hours?")
print(f"Agent: {chat('What are your hours?')}")
print()

print("=" * 50)
print("\nTEST 2 - Full Booking:")
print("Customer: Book grooming for Max")
print(f"Agent: {chat('Book grooming for Max on June 1st at 3pm number 9876543210')}")
print()

print("=" * 50)
print("\nTEST 3 - Services:")
print("Customer: What services do you offer?")
print(f"Agent: {chat('What services do you offer?')}")
print()

print("=" * 50)
print("\nTEST 4 - Unknown question:")
print("Customer: Do you accept senior dogs?")
print(f"Agent: {chat('Do you accept senior dogs?')}")
print()

print("=" * 50)
print("\nTEST 5 - Pricing:")
print("Customer: How much is King Suite?")
print(f"Agent: {chat('How much is the King Suite?')}")