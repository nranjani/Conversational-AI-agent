# test_booking.py

from tools.booking_tool import book_appointment

# Test 1 - Valid booking
print("TEST 1 - Valid Booking:")
result = book_appointment(
    "Max, Grooming, 2025-06-01, 3:00PM, 9876543210"
)
print(result)
print()

# Test 2 - Missing details
print("TEST 2 - Missing Details:")
result = book_appointment(
    "Max, Grooming"
)
print(result)
print()

# Test 3 - Another booking
print("TEST 3 - Another Booking:")
result = book_appointment(
    "Luna, Boarding, 2025-06-05, 10:00AM, 8765432109"
)
print(result)


from tools.email_tool import send_email_notification

print("TEST 4 - Email Notification:")
result = send_email_notification(
    "Pet: Max\n"
    "Service: Grooming\n"
    "Date: 2025-06-01\n"
    "Time: 3:00PM\n"
    "Phone: 9876543210"
)
print(result)


from tools.faq_tool import answer_faq

print()
print("TEST 5 - FAQ Hours:")
print(answer_faq("What are your hours?"))
print()

print("TEST 6 - FAQ Services:")
print(answer_faq("What services do you offer?"))
print()

print("TEST 7 - FAQ Price:")
print(answer_faq("What is the price?"))
print()

print("TEST 8 - FAQ Unknown:")
print(answer_faq("Do you accept credit cards?"))