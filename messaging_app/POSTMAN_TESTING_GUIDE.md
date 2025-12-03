# Postman API Testing Guide

## Overview
This guide documents the problems encountered while testing the Django REST API with Postman, the solutions implemented, and lessons learned for future development.

---

## 🔴 Problems Encountered & Solutions

### Problem 1: Phone Number Validation Failure
**Error**: `400 Bad Request`
```json
{"phone_number": ["Phone number must contain at least 10 digits"]}
```

**Root Cause**:
The phone number validation logic in `serializers.py` was stripping common phone number characters (`-`, ` `, `(`, `)`) but **not the `+` prefix** used in international phone numbers:
```python
cleaned = value.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
# Missing: .replace('+', '')
```

When Postman sent `"+1234567890"`, the validation saw `"+1234567890"` and `cleaned.isdigit()` returned `False` because of the `+`.

**Solution**:
```python
def validate_phone_number(self, value):
    """Validate phone number format"""
    if value:
        cleaned = value.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').replace('+', '')
        if not cleaned.isdigit() or len(cleaned) < 10:
            raise serializers.ValidationError("Phone number must contain at least 10 digits")
    return value
```

**Lesson Learned**:
- Always test validation logic with real-world data formats (international phone numbers, various formats)
- When stripping characters, consider all common variations (`+`, country codes, extensions)
- Use comprehensive test cases covering edge cases

---

### Problem 2: Conversation Creation Requires Minimum 2 Participants
**Error**: `400 Bad Request`
```json
{"participants_id": ["A conversation must have at least 2 participants"]}
```

**Root Cause**:
The Postman collection was sending only the current user's ID:
```json
{"participants_id": ["{{user_id}}"]}  // Only 1 participant
```

But the serializer validation required at least 2:
```python
if len(participants) < 2:
    raise serializers.ValidationError({
        "participants_id": "A conversation must have at least 2 participants"
    })
```

This created a catch-22: during testing with a single user account, you can't create a conversation.

**Solution**:
1. **Backend fix**: Allow 1 participant and automatically add the authenticated user:
```python
# Serializer validation
if len(participants) < 1:  # Changed from 2 to 1
    raise serializers.ValidationError({
        "participants_id": "A conversation must have at least 1 participant"
    })

# View create method
conversation.participants_id.add(request.user)  # Auto-add creator
conversation.participants_id.add(*participants)  # Add others
```

2. **Alternative solution**: Create multiple test users first, then reference them

**Lesson Learned**:
- Design APIs to be testable in isolation
- Consider single-user scenarios during development
- Auto-adding the authenticated user as a participant is a better UX
- Validation rules should support realistic testing scenarios

---

### Problem 3: Password Fields Not Required in Serializer
**Error**: `400 Bad Request` (passwords don't match or missing)

**Root Cause**:
Password fields were marked as `required=False` in the serializer:
```python
password = serializers.CharField(write_only=True, required=False, ...)
password_confirm = serializers.CharField(write_only=True, required=False, ...)
```

This allowed requests without passwords to pass serializer validation, but then failed in the view's password matching check.

**Solution**:
```python
password = serializers.CharField(write_only=True, required=True, ...)
password_confirm = serializers.CharField(write_only=True, required=True, ...)
```

Added explicit validation in the view:
```python
if not password or not password_confirm:
    return Response(
        {'error': 'Password and password confirmation are required'},
        status=status.HTTP_400_BAD_REQUEST
    )
```

**Lesson Learned**:
- Mark required fields as `required=True` in serializers
- Implement validation at the earliest point (serializer level before view logic)
- Provide clear error messages for missing required fields
- DRF serializer validation happens before view logic - use it!

---

### Problem 4: Postman Variables Not Set Between Iterations
**Error**: `401 Unauthorized` on all requests after first iteration

**Root Cause**:
When running Postman collections with **multiple iterations**:
- Iteration 1: Tries to register `testuser@example.com` ✅ Success
- Iteration 2: Tries to register `testuser@example.com` again ❌ **Email already exists**
- Iteration 3+: Same failure cascade

Additionally, the Login request was using a hardcoded email:
```json
{"email": "testuser@example.com", "password": "SecurePass123!"}
```

This didn't match the dynamically generated email from registration.

**Solution**:
1. **Generate unique emails per iteration** using pre-request script:
```javascript
// In Register User pre-request script
const timestamp = Date.now();
const randomNum = Math.floor(Math.random() * 10000);
const uniqueEmail = `testuser${timestamp}${randomNum}@example.com`;
pm.collectionVariables.set('test_email', uniqueEmail);
pm.collectionVariables.set('test_password', 'SecurePass123!');
```

2. **Use variables in request body**:
```json
{
    "email": "{{test_email}}",
    "password": "{{test_password}}",
    "password_confirm": "{{test_password}}",
    ...
}
```

3. **Update Login to use the same variables**:
```json
{
    "email": "{{test_email}}",
    "password": "{{test_password}}"
}
```

**Lesson Learned**:
- Use dynamic data generation for unique constraints (emails, usernames)
- Share variables between related requests
- Postman iterations run the ENTIRE collection multiple times
- Pre-request scripts run before each request, generating fresh data
- Test scripts save response data to variables for subsequent requests

---

### Problem 5: All Requests Fail After Registration Fails
**Error**: Cascade of `401 Unauthorized` errors

**Root Cause**:
When registration fails, the test script doesn't save the access token:
```javascript
if (pm.response.code === 201) {
    pm.collectionVariables.set('access_token', response.access);
    // ... only runs on success
}
```

Without a valid token, all subsequent requests (which require authentication) fail with `401 Unauthorized`.

**Solution**:
1. **Fix the root cause** (registration validation) so registration succeeds
2. **Add error logging** to test scripts:
```javascript
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.collectionVariables.set('access_token', response.access);
    pm.test('User registered successfully', () => {
        pm.expect(response.user).to.have.property('email');
    });
} else {
    console.log('Registration failed:', pm.response.text());
}
```

3. **Consider using Newman CLI** for better error visibility:
```bash
newman run messaging_api_collection.json \
    --iteration-count 5 \
    --delay-request 1000 \
    --reporters cli,json
```

**Lesson Learned**:
- A single failing request can break the entire collection flow
- Always log errors in test scripts for debugging
- Test each endpoint individually before running the full collection
- Use conditional logic in test scripts to handle failures gracefully

---

## 🔍 Debugging Strategies

### 1. Use Postman Console
**How**: `View` → `Show Postman Console` (or `Cmd+Option+C`)

**What to look for**:
- Request URLs, headers, and bodies
- Response status codes and bodies
- Console.log outputs from scripts
- Variable values at each step

**Add logging to scripts**:
```javascript
// Pre-request script (Collection level)
console.log('========================================');
console.log('Request:', pm.info.requestName);
console.log('URL:', pm.request.url.toString());
console.log('Variables:', {
    test_email: pm.collectionVariables.get('test_email'),
    access_token: pm.collectionVariables.get('access_token') ? 'SET' : 'NOT SET',
    user_id: pm.collectionVariables.get('user_id')
});

// Test script (Collection level)
console.log('Response Status:', pm.response.code);
console.log('Response Body:', pm.response.text().substring(0, 500));
console.log('========================================');
```

### 2. Test with cURL First
Before running Postman, test endpoints manually:

```bash
# 1. Test Registration
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Pass123!",
    "password_confirm": "Pass123!",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+1234567890",
    "role": "guest"
  }'

# 2. Test Login (copy token from response)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Pass123!"}'

# 3. Test Authenticated Endpoint
curl -X GET http://localhost:8000/api/conversations/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Benefits**:
- See exact error messages from Django
- Isolate problems to specific endpoints
- Faster iteration than Postman
- Easy to share commands with team

### 3. Check Django Server Logs
**Terminal output shows**:
- Request method, path, and status code
- Warnings and errors
- Database queries (with `DEBUG=True`)

**Example**:
```
Bad Request: /api/auth/register/
[03/Dec/2025 02:46:13] "POST /api/auth/register/ HTTP/1.1" 400 65
```

**Enable detailed logging** in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### 4. Use Django's Test Framework
Create unit tests alongside Postman tests:

```python
# chats/tests.py
from rest_framework.test import APITestCase
from rest_framework import status

class AuthenticationTests(APITestCase):
    def test_register_user(self):
        data = {
            'email': 'test@example.com',
            'password': 'Pass123!',
            'password_confirm': 'Pass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+1234567890',
            'role': 'guest'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
```

Run tests:
```bash
python manage.py test chats.tests.AuthenticationTests
```

### 5. Test Individual Requests First
Don't run the entire collection immediately:
1. ✅ Test Register User alone
2. ✅ Test Login alone (after manual registration)
3. ✅ Test Create Conversation (with saved token)
4. ✅ Test Send Message
5. ✅ Then run full collection

---

## ✅ Best Practices for API Testing

### 1. Design for Testability
**Do**:
- Auto-populate fields like `sender_id` from authenticated user
- Allow single-user testing scenarios
- Return detailed error messages with field names
- Use meaningful HTTP status codes

**Don't**:
- Require manual IDs that don't exist yet
- Force multi-user scenarios in isolation
- Return generic "Bad Request" without details

### 2. Use Collection Variables Effectively
```javascript
// Save important values
pm.collectionVariables.set('access_token', response.access);
pm.collectionVariables.set('user_id', response.user.user_id);
pm.collectionVariables.set('conversation_id', response.conversation_id);

// Use them in subsequent requests
// URL: {{base_url}}/conversations/{{conversation_id}}/
// Header: Authorization: Bearer {{access_token}}
```

### 3. Handle Failures Gracefully
```javascript
// Test script with error handling
if (pm.response.code === 201) {
    // Success path
    const response = pm.response.json();
    pm.collectionVariables.set('conversation_id', response.conversation_id);
    pm.test('Conversation created', () => {
        pm.expect(response).to.have.property('conversation_id');
    });
} else {
    // Failure path
    console.error('Failed to create conversation:', pm.response.text());
    pm.test('Conversation creation failed', () => {
        pm.expect.fail('Got status ' + pm.response.code);
    });
}
```

### 4. Validate Response Structure
```javascript
pm.test('Response has pagination', () => {
    const response = pm.response.json();
    pm.expect(response).to.have.property('count');
    pm.expect(response).to.have.property('next');
    pm.expect(response).to.have.property('previous');
    pm.expect(response).to.have.property('results');
    pm.expect(response.results).to.be.an('array');
});
```

### 5. Use Iteration Delays
When running multiple iterations:
```javascript
// Collection settings
{
    "iterations": 10,
    "delay": 1000  // 1 second between requests
}
```

Or with Newman:
```bash
newman run collection.json \
    --iteration-count 10 \
    --delay-request 1000
```

---

## 📋 Common HTTP Status Codes & Meanings

| Code | Status | Meaning | Common Causes |
|------|--------|---------|---------------|
| 200 | OK | Request succeeded | GET, PUT, PATCH successful |
| 201 | Created | Resource created | POST successful |
| 400 | Bad Request | Invalid data | Validation errors, missing fields |
| 401 | Unauthorized | Authentication required | Missing/invalid token |
| 403 | Forbidden | Permission denied | Valid token but insufficient permissions |
| 404 | Not Found | Resource doesn't exist | Wrong URL or deleted resource |
| 500 | Internal Server Error | Server-side error | Bugs, database errors |

---

## 🛠️ Quick Troubleshooting Checklist

### Registration Failing?
- [ ] Check phone number format (does it have special characters?)
- [ ] Verify all required fields are present
- [ ] Check password and password_confirm match
- [ ] Verify email is unique (not already registered)

### Login Failing?
- [ ] Verify email matches a registered user
- [ ] Check password is correct
- [ ] Ensure using the same email from registration (if dynamic)

### Authenticated Endpoints Failing (401)?
- [ ] Check access_token variable is set
- [ ] Verify token hasn't expired (60-minute default)
- [ ] Ensure Authorization header format: `Bearer {{access_token}}`

### Conversation/Message Creation Failing?
- [ ] Verify user is authenticated
- [ ] Check conversation_id exists and is valid UUID
- [ ] Ensure user is a participant in the conversation
- [ ] Verify all required fields are present

### Tests Failing on Iterations?
- [ ] Check for unique constraint violations (duplicate emails)
- [ ] Verify variables are being set in test scripts
- [ ] Ensure pre-request scripts generate unique data
- [ ] Check collection variable scope (collection vs. environment)

---

## 🎯 Key Takeaways

1. **Validation is Critical**: Test with real-world data formats, not just happy paths
2. **Design for Single-User Testing**: Allow development/testing with one account
3. **Use Dynamic Data**: Generate unique values for each iteration
4. **Log Everything**: Use console.log liberally during debugging
5. **Test Incrementally**: Verify each endpoint before testing the full flow
6. **Read Error Messages**: Django provides detailed validation errors - use them!
7. **Share Variables**: Use collection variables to pass data between requests
8. **Handle Failures**: Add error handling to prevent cascade failures

---

## 🔰 Common Beginner Mistakes & How to Avoid Them

### Mistake 1: Not Starting the Django Server
**Symptom**: `curl: (7) Failed to connect to localhost port 8000`

**Why it happens**: Forgetting to run the development server before testing.

**Solution**:
```bash
# Always start server first
cd messaging_app
python manage.py runserver 8000

# Keep it running in a separate terminal window
```

**Pro Tip**: Use `screen` or `tmux` to keep server running in background:
```bash
# Start in background
python manage.py runserver 8000 > /tmp/django.log 2>&1 &

# Check if running
ps aux | grep runserver

# View logs
tail -f /tmp/django.log
```

---

### Mistake 2: Wrong Content-Type Header
**Symptom**: `400 Bad Request` or empty request body

**Why it happens**: Django REST Framework expects JSON but receives form data.

**Wrong**:
```javascript
// Postman Headers tab: Content-Type: application/x-www-form-urlencoded
```

**Correct**:
```javascript
// Postman Headers tab
Content-Type: application/json

// Body tab: Select "raw" and "JSON"
{
    "email": "test@example.com",
    "password": "Pass123!"
}
```

**In Postman**: Always set Body type to **"raw"** and select **"JSON"** from dropdown.

---

### Mistake 3: Using Environment Variables Instead of Collection Variables
**Symptom**: Variables not persisting between requests

**Why it happens**: Mixing variable scopes.

**Variable Scopes** (from most specific to most general):
1. **Local** - Only within a single request
2. **Collection** - Shared across all requests in the collection ✅ **USE THIS**
3. **Environment** - Shared across multiple collections
4. **Global** - Shared across all environments

**Correct Usage**:
```javascript
// Set variable (use collection scope for most cases)
pm.collectionVariables.set('access_token', token);

// Get variable
pm.collectionVariables.get('access_token');

// NOT: pm.environment.set() or pm.globals.set()
```

---

### Mistake 4: Forgetting to Save Tokens in Test Scripts
**Symptom**: All requests after login fail with 401

**Why it happens**: Registration/login succeeds but token isn't saved.

**Wrong**:
```javascript
// Test script - NO TOKEN SAVING
pm.test('Login successful', () => {
    pm.expect(pm.response.code).to.equal(200);
    // Token is lost! ❌
});
```

**Correct**:
```javascript
// Test script - SAVE TOKEN
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.collectionVariables.set('access_token', response.access); // ✅
    pm.collectionVariables.set('user_id', response.user.user_id);  // ✅
}
```

**Remember**: If you don't save it, you lose it!

---

### Mistake 5: Using {{variable}} in JavaScript Code
**Symptom**: `ReferenceError: variable is not defined`

**Why it happens**: Confusing Postman variable syntax in different contexts.

**Wrong**:
```javascript
// In Pre-request or Test Script
const email = {{test_email}};  // ❌ Syntax error
const url = {{base_url}}/users; // ❌ Won't work
```

**Correct**:
```javascript
// In Pre-request or Test Script - use pm.variables.get()
const email = pm.collectionVariables.get('test_email'); // ✅
const url = pm.collectionVariables.get('base_url') + '/users'; // ✅

// In Request URL, Headers, or Body - use {{variable}}
// URL: {{base_url}}/auth/login/  ✅
// Body: {"email": "{{test_email}}"}  ✅
```

**Rule**: `{{variable}}` syntax only works in request configuration (URL, headers, body). Use `pm.variables.get()` in scripts.

---

### Mistake 6: Not Checking Response Status Before Processing
**Symptom**: Test scripts crash with "Cannot read property of undefined"

**Why it happens**: Trying to access response.data when request failed.

**Wrong**:
```javascript
// Test script - NO STATUS CHECK
const response = pm.response.json(); // ❌ Crashes if not JSON
pm.collectionVariables.set('user_id', response.user.user_id); // ❌ Undefined error
```

**Correct**:
```javascript
// Test script - WITH STATUS CHECK
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.collectionVariables.set('user_id', response.user.user_id); // ✅ Safe
    pm.test('Success', () => pm.expect(response).to.have.property('user'));
} else {
    console.error('Failed:', pm.response.text()); // ✅ Debug failed requests
}
```

---

### Mistake 7: Hardcoding Test Data
**Symptom**: Tests fail on second run with "email already exists"

**Why it happens**: Using same test data repeatedly.

**Wrong**:
```json
{
    "email": "test@example.com",
    "password": "Pass123!"
}
```
Running twice → Second attempt fails because email exists.

**Correct**:
```javascript
// Pre-request Script
const timestamp = Date.now();
const randomNum = Math.floor(Math.random() * 10000);
pm.collectionVariables.set('test_email', `user${timestamp}${randomNum}@example.com`);

// Request Body
{
    "email": "{{test_email}}",
    "password": "Pass123!"
}
```

**Pro Tip**: Use faker library for realistic test data:
```javascript
// In Pre-request Script (requires Postman version with faker)
const faker = require('faker');
pm.collectionVariables.set('first_name', faker.name.firstName());
pm.collectionVariables.set('last_name', faker.name.lastName());
pm.collectionVariables.set('email', faker.internet.email());
```

---

### Mistake 8: Wrong Authentication Header Format
**Symptom**: 401 Unauthorized despite having valid token

**Why it happens**: Missing "Bearer" prefix or extra spaces.

**Wrong**:
```
Authorization: {{access_token}}  ❌
Authorization: Bearer{{access_token}}  ❌
Authorization: Token {{access_token}}  ❌
```

**Correct**:
```
Authorization: Bearer {{access_token}}  ✅
```

**Note**: Exactly one space between "Bearer" and the token!

---

### Mistake 9: Not Using Request Order
**Symptom**: Trying to create messages before conversations exist

**Why it happens**: Requests run in wrong order.

**Collection Structure** (correct order):
```
1. Authentication
   ├── Register User      (saves access_token, user_id)
   ├── Login             (updates access_token)
   
2. Conversations
   ├── Create Conversation (saves conversation_id)
   ├── List Conversations
   
3. Messages
   ├── Send Message       (uses conversation_id)
   ├── List Messages
```

**Important**: Postman runs requests **top to bottom** in a collection. Organize accordingly!

---

### Mistake 10: Ignoring Django Migrations
**Symptom**: Various database errors, "relation does not exist"

**Why it happens**: Database schema doesn't match models.

**When to run migrations**:
- After changing models.py
- After pulling code from git
- When getting database errors

**How to fix**:
```bash
# Always do these in order
python manage.py makemigrations
python manage.py migrate

# Verify migrations are applied
python manage.py showmigrations

# If really stuck, reset database (DELETES ALL DATA!)
rm db.sqlite3
python manage.py migrate
```

---

### Mistake 11: Not Reading Error Messages
**Symptom**: Repeatedly making the same mistake

**Why it happens**: Ignoring valuable feedback from Django.

**Example Error Message**:
```json
{
    "phone_number": ["Phone number must contain at least 10 digits"],
    "email": ["user with this email already exists."]
}
```

**Each field** tells you exactly what's wrong! Read them carefully.

**Pro Tip**: Keep Postman Console open to see full error messages:
```javascript
// Add to test script
if (pm.response.code >= 400) {
    console.error('❌ Request failed:');
    console.error('Status:', pm.response.code);
    console.error('Response:', pm.response.text());
}
```

---

### Mistake 12: Not Understanding JWT Token Expiration
**Symptom**: Tests pass initially, then fail with 401 after an hour

**Why it happens**: JWT access tokens expire (default 60 minutes).

**Solution Options**:

**Option 1**: Extend token lifetime (for development only):
```python
# settings.py
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),  # Instead of 60 minutes
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

**Option 2**: Re-login when token expires:
```javascript
// Test script - check for token expiration
if (pm.response.code === 401) {
    console.log('Token expired, need to re-login');
    // Trigger login request
}
```

**Option 3**: Use refresh token endpoint:
```javascript
// When access token expires, refresh it
POST /api/auth/token/refresh/
{
    "refresh": "{{refresh_token}}"
}
```

---

### Mistake 13: Running Tests Without Delay
**Symptom**: Database lock errors, race conditions

**Why it happens**: Hitting API too fast without letting requests complete.

**Wrong**:
```javascript
// Collection settings
Iterations: 100
Delay: 0 ms  // ❌ Too fast!
```

**Correct**:
```javascript
// Collection settings
Iterations: 10
Delay: 1000 ms  // ✅ 1 second between requests
```

**For Production-like Testing**:
```javascript
Iterations: 5
Delay: 2000 ms  // 2 seconds - more realistic user behavior
```

---

### Mistake 14: Not Cleaning Up Test Data
**Symptom**: Database fills up with test data, tests become slow

**Why it happens**: Creating data but never deleting it.

**Solutions**:

**Option 1**: Use a separate test database:
```bash
# In settings.py for testing
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'test_db.sqlite3',  # Separate DB
        }
    }
```

**Option 2**: Add cleanup requests to collection:
```javascript
// Last request in collection
DELETE /api/conversations/{{conversation_id}}/
DELETE /api/users/{{user_id}}/
```

**Option 3**: Reset database periodically:
```bash
# Quick reset (DELETES ALL DATA!)
rm db.sqlite3
python manage.py migrate
```

---

### Mistake 15: Mixing Python Virtual Environments
**Symptom**: `ModuleNotFoundError: No module named 'rest_framework'`

**Why it happens**: Running Django with wrong Python environment.

**Check active environment**:
```bash
which python
# Should show: .../alx-backend-python/.venv/bin/python

pip list | grep djangorestframework
# Should show: djangorestframework    x.x.x
```

**Fix**:
```bash
# Activate correct virtual environment
source .venv/bin/activate

# Verify packages are installed
pip install -r requirements.txt
```

**Pro Tip**: Always see `(.venv)` at start of terminal prompt.

---

### Mistake 16: Not Version Controlling Postman Collections
**Symptom**: Losing collection changes, team members have different versions

**Why it happens**: Only keeping collection in Postman app.

**Best Practice**:
```bash
# Export collection to JSON
git add messaging_api_collection.json
git commit -m "feat: add message filtering to Postman collection"
git push
```

**Benefits**:
- Team members can import latest version
- Track changes over time
- Backup if Postman loses data
- Review collection changes in PRs

---

### Mistake 17: Forgetting CORS for Frontend Testing
**Symptom**: Browser console shows "CORS policy" errors

**Why it happens**: Django blocks cross-origin requests by default.

**Fix** (for development only):
```python
# settings.py
INSTALLED_APPS = [
    'corsheaders',  # Install: pip install django-cors-headers
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be early
    ...
]

# Development only!
CORS_ALLOW_ALL_ORIGINS = True
```

**Production**: Configure specific allowed origins:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "https://myapp.com",
]
```

---

### Mistake 18: Not Using Postman's Built-in Test Snippets
**Symptom**: Writing repetitive test code from scratch

**Why it happens**: Not knowing about built-in snippets.

**Where to find**: Right side of Postman's "Tests" tab → Click snippets:
- ✅ "Status code: Code is 200"
- ✅ "Response body: JSON value check"
- ✅ "Response time is less than 200ms"

**Example**: Click "Status code: Code is 201" → Instantly adds:
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});
```

**Pro Tip**: Customize snippets after inserting them!

---

### Mistake 19: Testing in Production
**Symptom**: Breaking live data, angry users

**Why it happens**: Pointing Postman to production URL.

**Prevention**:
```javascript
// Use environment variables
// Environment: Development
{
    "base_url": "http://localhost:8000/api"
}

// Environment: Production
{
    "base_url": "https://api.production.com"
}
```

**In Postman**: Top-right corner → Select "Development" environment.

**Safety Check**: Add to collection pre-request:
```javascript
const baseUrl = pm.collectionVariables.get('base_url');
if (baseUrl.includes('production.com')) {
    throw new Error('⚠️  STOP! You are testing on PRODUCTION!');
}
```

---

### Mistake 20: Not Learning from Server Logs
**Symptom**: Repeating mistakes, not understanding what Django is doing

**Why it happens**: Only looking at Postman, ignoring Django terminal.

**What to watch for**:
```bash
# Terminal Output
[03/Dec/2025 02:58:41] "POST /api/auth/register/ HTTP/1.1" 400 65
                        ^^^^                                ^^^
                        Method + URL                        Status + Size
```

**Status Code Meanings**:
- `2xx` = Success ✅
- `4xx` = Client error (your problem) ❌
- `5xx` = Server error (Django's problem) 🔥

**Enable Debug Mode** (development only):
```python
# settings.py
DEBUG = True  # Shows detailed error pages
```

---

## 🎓 Learning Checklist for Beginners

Before running your first Postman collection, make sure you understand:

- [ ] How to start Django development server
- [ ] Difference between GET, POST, PUT, DELETE methods
- [ ] What JSON is and how to format it
- [ ] How to read HTTP status codes (200, 400, 401, 404, 500)
- [ ] What authentication tokens are and how they work
- [ ] How to use Postman Console for debugging
- [ ] Difference between Headers and Body in requests
- [ ] How to save and use collection variables
- [ ] What a pre-request script does vs. a test script
- [ ] How to read Django error messages
- [ ] When to run migrations
- [ ] How to activate Python virtual environment
- [ ] What CRUD operations are (Create, Read, Update, Delete)
- [ ] How to use cURL as an alternative to Postman
- [ ] Where to find API documentation (README, comments, code)

**Pro Tip**: Master one endpoint at a time before moving to complex workflows!

---

## 📚 Additional Resources

- [Postman Documentation](https://learning.postman.com/docs/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Newman CLI Documentation](https://learning.postman.com/docs/running-collections/using-newman-cli/command-line-integration-with-newman/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [Understanding JWT Tokens](https://jwt.io/introduction)
- [REST API Best Practices](https://restfulapi.net/)

---

## 🚀 Running the Tests

### With Postman GUI:
1. Import `messaging_api_collection.json`
2. Ensure Django server is running: `python manage.py runserver 8000`
3. Open Collection Runner
4. Select the collection
5. Set iterations (e.g., 5) and delay (e.g., 1000ms)
6. Click "Run"
7. Open Postman Console to see detailed logs

### With Newman CLI:
```bash
# Install Newman
npm install -g newman

# Run collection
newman run messaging_api_collection.json \
    --iteration-count 5 \
    --delay-request 1000 \
    --reporters cli,json \
    --reporter-json-export results.json

# Run with environment
newman run messaging_api_collection.json \
    --environment production.postman_environment.json \
    --iteration-count 10
```

---

**Last Updated**: December 3, 2025
**Django Version**: 5.2.8
**DRF Version**: 3.14.0
**Python Version**: 3.13.7
