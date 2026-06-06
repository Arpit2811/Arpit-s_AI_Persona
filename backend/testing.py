import requests

response = requests.post(
    "https://mephitically-cytopathogenic-maritza.ngrok-free.dev/book-interview",
    json={
        "name": "Puma Gaming",
        "email": "pumagaming62@gmail.com",
        "date": "2026-06-10",
        "time": "14:00",
        "subject": "AI Engineer Interview",
        "body": "Discussion regarding GenAI Engineer opportunity."
    }
)

print(response.status_code)
print(response.text)