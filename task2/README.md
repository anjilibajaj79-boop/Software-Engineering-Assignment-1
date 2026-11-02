
# Task 2 - Secure Text Processing API

## Project Description
This project develops a Flask REST API that processes text into uppercase.
The API uses three unique API keys to authenticate different consumers.

## Technologies Used
- Python
- Flask
- REST API
- JSON
- API Key Authentication
- cURL

## API Endpoint
POST /process

Local URL:
http://127.0.0.1:5001/process

## Request Headers
Content-Type: application/json
X-API-Key: YOUR_API_KEY

## Request Body
{
    "text": "hello world"
}

## Successful Response
{
    "message": "Text processed successfully",
    "processed_text": "HELLO WORLD"
}

## Security Features
- Three unique API keys are generated.
- API keys are sent through the X-API-Key header.
- Invalid API keys are rejected.
- Missing API keys are rejected.
- Unauthorized requests receive HTTP 401.

## Testing
The API was tested using PowerShell and cURL.
All three valid consumer keys were tested.
Invalid and missing API key requests were also tested.
