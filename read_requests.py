import requests

def read(r):
    print("RESPONSE VALUES")
    print(f"Response: {r}")
    print(f"Reason: {r.reason}")
    print(f"Request: {r.request}")
    print(f"Content: {r.content}")
    print(f"URL: {r.url}")
    print(f"Headers: {r.headers}")
    print(f"Status Code: {r.status_code}")