# Task 3 - Employee Management API

## Project Description
An Employee Management REST API developed using Python, Flask and SQLite.

## Technologies Used
- Python
- Flask
- SQLite
- REST API
- JSON
- Authentication
- Role-Based Authorization

## API Endpoints

| Method | Endpoint | Permission |
|--------|----------|------------|
| POST | /login | All users |
| GET | /employees | Admin and Employee |
| POST | /employees | Administrator |
| PUT | /employees/<id> | Administrator |
| DELETE | /employees/<id> | Administrator |

## User Roles

Administrator:
- View employees
- Add employees
- Update employees
- Delete employees

Employee:
- View employees only

## Security
- Login authentication
- Temporary token generation
- Role-based authorization
- HTTP 401 for unauthorized requests
- HTTP 403 for forbidden actions

## Testing
Tested using PowerShell:
- Admin login
- Employee login
- Admin CRUD operations
- Employee access restrictions
- Invalid password