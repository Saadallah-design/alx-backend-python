# How to Write a Postman Collection JSON File

## 📖 Table of Contents
1. [Introduction](#introduction)
2. [Postman Collection Structure](#postman-collection-structure)
3. [Building Your First Collection](#building-your-first-collection)
4. [Collection Variables](#collection-variables)
5. [Creating Requests](#creating-requests)
6. [Pre-request Scripts](#pre-request-scripts)
7. [Test Scripts](#test-scripts)
8. [Advanced Features](#advanced-features)
9. [Best Practices](#best-practices)
10. [Complete Example](#complete-example)

---

## Introduction

A Postman Collection is a JSON file that defines:
- **Requests**: API endpoints you want to test
- **Variables**: Dynamic data shared across requests
- **Scripts**: JavaScript code to automate testing
- **Tests**: Assertions to verify API behavior

**Why use JSON files?**
- ✅ Version control (Git-friendly)
- ✅ Team collaboration
- ✅ Automation with Newman CLI
- ✅ Reproducible tests

---

## Postman Collection Structure

### Basic Structure
```json
{
  "info": {
    "_postman_id": "unique-id-here",
    "name": "My API Collection",
    "description": "Collection description",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    // Collection variables go here
  ],
  "item": [
    // Requests and folders go here
  ]
}
```

### Key Sections Explained

#### 1. **Info Section** - Collection Metadata
```json
"info": {
  "_postman_id": "abc-123-def-456",  // Unique identifier
  "name": "Messaging API",            // Display name
  "description": "REST API for messaging app",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
}
```

#### 2. **Variable Section** - Shared Data
```json
"variable": [
  {
    "key": "base_url",
    "value": "http://localhost:8000/api",
    "type": "string"
  },
  {
    "key": "access_token",
    "value": "",  // Empty initially, filled by scripts
    "type": "string"
  }
]
```

#### 3. **Item Section** - Requests
```json
"item": [
  {
    "name": "Login",
    "request": {
      "method": "POST",
      "header": [],
      "body": {},
      "url": {}
    }
  }
]
```

---

## Building Your First Collection

### Step 1: Create the Shell

Start with this minimal template:

```json
{
  "info": {
    "_postman_id": "my-first-collection-001",
    "name": "My First API Collection",
    "description": "Learning to write Postman collections",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [],
  "item": []
}
```

**Save as**: `my_collection.json`

### Step 2: Add Base URL Variable

```json
{
  "info": { ... },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000/api",
      "type": "string"
    }
  ],
  "item": []
}
```

**Why?** Change URL once instead of in every request.

### Step 3: Add Your First Request

```json
{
  "info": { ... },
  "variable": [ ... ],
  "item": [
    {
      "name": "Get Users",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/users/",
          "host": ["{{base_url}}"],
          "path": ["users", ""]
        }
      },
      "response": []
    }
  ]
}
```

**Test it**: Import into Postman → Send request

---

## Collection Variables

Variables store data that changes or is reused across requests.

### Defining Variables

```json
"variable": [
  {
    "key": "base_url",
    "value": "http://localhost:8000/api",
    "type": "string"
  },
  {
    "key": "access_token",
    "value": "",
    "type": "string"
  },
  {
    "key": "user_id",
    "value": "",
    "type": "string"
  }
]
```

### Using Variables in Requests

**In URL**:
```json
"url": {
  "raw": "{{base_url}}/users/{{user_id}}/"
}
```

**In Headers**:
```json
"header": [
  {
    "key": "Authorization",
    "value": "Bearer {{access_token}}"
  }
]
```

**In Request Body**:
```json
"body": {
  "mode": "raw",
  "raw": "{\n  \"email\": \"{{test_email}}\",\n  \"password\": \"{{test_password}}\"\n}"
}
```

### Setting Variables in Scripts

```javascript
// Set a variable
pm.collectionVariables.set('access_token', 'eyJhbGc...');

// Get a variable
const token = pm.collectionVariables.get('access_token');

// Delete a variable
pm.collectionVariables.unset('access_token');
```

---

## Creating Requests

### Request Structure

```json
{
  "name": "Request Name",
  "event": [
    // Pre-request and test scripts
  ],
  "request": {
    "method": "GET|POST|PUT|DELETE|PATCH",
    "header": [
      // HTTP headers
    ],
    "body": {
      // Request body (for POST/PUT/PATCH)
    },
    "url": {
      // URL configuration
    }
  },
  "response": []
}
```

### GET Request Example

```json
{
  "name": "List Messages",
  "request": {
    "method": "GET",
    "header": [
      {
        "key": "Authorization",
        "value": "Bearer {{access_token}}",
        "type": "text"
      }
    ],
    "url": {
      "raw": "{{base_url}}/messages/?page=1",
      "host": ["{{base_url}}"],
      "path": ["messages", ""],
      "query": [
        {
          "key": "page",
          "value": "1"
        }
      ]
    }
  },
  "response": []
}
```

### POST Request Example

```json
{
  "name": "Create User",
  "request": {
    "method": "POST",
    "header": [
      {
        "key": "Content-Type",
        "value": "application/json"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n  \"email\": \"user@example.com\",\n  \"password\": \"Pass123!\",\n  \"first_name\": \"John\",\n  \"last_name\": \"Doe\"\n}"
    },
    "url": {
      "raw": "{{base_url}}/users/",
      "host": ["{{base_url}}"],
      "path": ["users", ""]
    }
  },
  "response": []
}
```

**Tip**: Use `\n` for line breaks in JSON strings.

### PUT/PATCH Request Example

```json
{
  "name": "Update User",
  "request": {
    "method": "PATCH",
    "header": [
      {
        "key": "Authorization",
        "value": "Bearer {{access_token}}"
      },
      {
        "key": "Content-Type",
        "value": "application/json"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n  \"first_name\": \"Jane\"\n}"
    },
    "url": {
      "raw": "{{base_url}}/users/{{user_id}}/",
      "host": ["{{base_url}}"],
      "path": ["users", "{{user_id}}", ""]
    }
  },
  "response": []
}
```

### DELETE Request Example

```json
{
  "name": "Delete User",
  "request": {
    "method": "DELETE",
    "header": [
      {
        "key": "Authorization",
        "value": "Bearer {{access_token}}"
      }
    ],
    "url": {
      "raw": "{{base_url}}/users/{{user_id}}/",
      "host": ["{{base_url}}"],
      "path": ["users", "{{user_id}}", ""]
    }
  },
  "response": []
}
```

---

## Pre-request Scripts

Pre-request scripts run **before** a request is sent. Use them to:
- Generate dynamic data
- Set variables
- Prepare authentication
- Add timestamps

### Script Structure

```json
{
  "name": "Register User",
  "event": [
    {
      "listen": "prerequest",
      "script": {
        "exec": [
          "// JavaScript code here",
          "const timestamp = Date.now();",
          "pm.collectionVariables.set('timestamp', timestamp);"
        ],
        "type": "text/javascript"
      }
    }
  ],
  "request": { ... }
}
```

**Important**: Each line is a separate string in the `exec` array.

### Common Pre-request Script Examples

#### Generate Unique Email
```json
"script": {
  "exec": [
    "// Generate unique email for testing",
    "const timestamp = Date.now();",
    "const randomNum = Math.floor(Math.random() * 10000);",
    "const email = `testuser${timestamp}${randomNum}@example.com`;",
    "pm.collectionVariables.set('test_email', email);"
  ],
  "type": "text/javascript"
}
```

#### Add Current Timestamp
```json
"script": {
  "exec": [
    "// Add current timestamp",
    "const now = new Date().toISOString();",
    "pm.collectionVariables.set('current_time', now);",
    "console.log('Current time:', now);"
  ],
  "type": "text/javascript"
}
```

#### Generate Random Data
```json
"script": {
  "exec": [
    "// Generate random test data",
    "const firstNames = ['John', 'Jane', 'Bob', 'Alice'];",
    "const lastNames = ['Smith', 'Doe', 'Johnson', 'Williams'];",
    "",
    "const randomFirst = firstNames[Math.floor(Math.random() * firstNames.length)];",
    "const randomLast = lastNames[Math.floor(Math.random() * lastNames.length)];",
    "",
    "pm.collectionVariables.set('first_name', randomFirst);",
    "pm.collectionVariables.set('last_name', randomLast);"
  ],
  "type": "text/javascript"
}
```

#### Check if Token Exists
```json
"script": {
  "exec": [
    "// Check if we have a valid token",
    "const token = pm.collectionVariables.get('access_token');",
    "",
    "if (!token) {",
    "    console.warn('⚠️ No access token found. Please login first.');",
    "}"
  ],
  "type": "text/javascript"
}
```

---

## Test Scripts

Test scripts run **after** a response is received. Use them to:
- Validate responses
- Save data to variables
- Run assertions
- Log debugging info

### Script Structure

```json
{
  "name": "Login",
  "event": [
    {
      "listen": "test",
      "script": {
        "exec": [
          "// JavaScript code here",
          "if (pm.response.code === 200) {",
          "    const response = pm.response.json();",
          "    pm.collectionVariables.set('access_token', response.access);",
          "}"
        ],
        "type": "text/javascript"
      }
    }
  ],
  "request": { ... }
}
```

### Common Test Script Examples

#### Basic Status Code Check
```json
"script": {
  "exec": [
    "pm.test('Status code is 200', function () {",
    "    pm.response.to.have.status(200);",
    "});"
  ],
  "type": "text/javascript"
}
```

#### Save Response Data to Variables
```json
"script": {
  "exec": [
    "if (pm.response.code === 201) {",
    "    const response = pm.response.json();",
    "    ",
    "    // Save important IDs",
    "    pm.collectionVariables.set('user_id', response.user.user_id);",
    "    pm.collectionVariables.set('access_token', response.access);",
    "    pm.collectionVariables.set('refresh_token', response.refresh);",
    "    ",
    "    console.log('✅ User registered:', response.user.email);",
    "}"
  ],
  "type": "text/javascript"
}
```

#### Validate Response Structure
```json
"script": {
  "exec": [
    "pm.test('Response has required fields', function () {",
    "    const response = pm.response.json();",
    "    pm.expect(response).to.have.property('user_id');",
    "    pm.expect(response).to.have.property('email');",
    "    pm.expect(response).to.have.property('created_at');",
    "});"
  ],
  "type": "text/javascript"
}
```

#### Check Response Time
```json
"script": {
  "exec": [
    "pm.test('Response time is less than 500ms', function () {",
    "    pm.expect(pm.response.responseTime).to.be.below(500);",
    "});"
  ],
  "type": "text/javascript"
}
```

#### Validate Array Response
```json
"script": {
  "exec": [
    "pm.test('Response is an array', function () {",
    "    const response = pm.response.json();",
    "    pm.expect(response.results).to.be.an('array');",
    "    pm.expect(response.results.length).to.be.at.least(1);",
    "});"
  ],
  "type": "text/javascript"
}
```

#### Handle Success and Failure
```json
"script": {
  "exec": [
    "if (pm.response.code === 200) {",
    "    // Success path",
    "    const response = pm.response.json();",
    "    pm.test('Login successful', function () {",
    "        pm.expect(response).to.have.property('access');",
    "    });",
    "    pm.collectionVariables.set('access_token', response.access);",
    "} else {",
    "    // Failure path",
    "    console.error('❌ Login failed:', pm.response.text());",
    "    pm.test('Login failed - check credentials', function () {",
    "        pm.expect.fail('Got status ' + pm.response.code);",
    "    });",
    "}"
  ],
  "type": "text/javascript"
}
```

---

## Advanced Features

### Organizing with Folders

Group related requests in folders:

```json
"item": [
  {
    "name": "Authentication",
    "item": [
      {
        "name": "Register",
        "request": { ... }
      },
      {
        "name": "Login",
        "request": { ... }
      }
    ]
  },
  {
    "name": "Users",
    "item": [
      {
        "name": "List Users",
        "request": { ... }
      },
      {
        "name": "Get User",
        "request": { ... }
      }
    ]
  }
]
```

**Benefits**:
- Better organization
- Easier navigation
- Logical grouping
- Can run folder separately

### Collection-Level Scripts

Add scripts that run for ALL requests:

```json
{
  "info": { ... },
  "event": [
    {
      "listen": "prerequest",
      "script": {
        "exec": [
          "// Runs before EVERY request",
          "console.log('===================================');",
          "console.log('Request:', pm.info.requestName);",
          "console.log('URL:', pm.request.url.toString());"
        ],
        "type": "text/javascript"
      }
    },
    {
      "listen": "test",
      "script": {
        "exec": [
          "// Runs after EVERY request",
          "console.log('Status:', pm.response.code);",
          "console.log('Time:', pm.response.responseTime + 'ms');",
          "console.log('===================================');"
        ],
        "type": "text/javascript"
      }
    }
  ],
  "variable": [ ... ],
  "item": [ ... ]
}
```

### Query Parameters

Add query strings to URLs:

```json
"url": {
  "raw": "{{base_url}}/messages/?page={{page}}&limit={{limit}}",
  "host": ["{{base_url}}"],
  "path": ["messages", ""],
  "query": [
    {
      "key": "page",
      "value": "{{page}}",
      "description": "Page number"
    },
    {
      "key": "limit",
      "value": "{{limit}}",
      "description": "Items per page"
    },
    {
      "key": "search",
      "value": "test",
      "disabled": true,  // This param is not sent
      "description": "Search term"
    }
  ]
}
```

### Authentication

#### Bearer Token (Most Common)
```json
"request": {
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{access_token}}",
        "type": "string"
      }
    ]
  },
  "method": "GET",
  "header": [],
  "url": { ... }
}
```

**Alternative**: Add to headers manually:
```json
"header": [
  {
    "key": "Authorization",
    "value": "Bearer {{access_token}}",
    "type": "text"
  }
]
```

#### Basic Auth
```json
"auth": {
  "type": "basic",
  "basic": [
    {
      "key": "username",
      "value": "{{username}}",
      "type": "string"
    },
    {
      "key": "password",
      "value": "{{password}}",
      "type": "string"
    }
  ]
}
```

### Request Descriptions

Add helpful documentation:

```json
{
  "name": "Create Message",
  "request": {
    "description": "Creates a new message in a conversation.\n\n**Required Fields:**\n- conversation_id (UUID)\n- message_body (string)\n\n**Headers:**\n- Authorization: Bearer token required\n\n**Example Response:**\n```json\n{\n  \"message_id\": \"abc-123\",\n  \"message_body\": \"Hello!\",\n  \"sent_at\": \"2025-12-03T10:30:00Z\"\n}\n```",
    "method": "POST",
    "header": [ ... ],
    "body": { ... },
    "url": { ... }
  }
}
```

---

## Best Practices

### 1. Use Meaningful Names

**Bad**:
```json
{"name": "Request 1"}
{"name": "Test 2"}
{"name": "API Call"}
```

**Good**:
```json
{"name": "Register New User"}
{"name": "Login with Email"}
{"name": "Get User Profile"}
```

### 2. Organize with Folders

```
📁 My API Collection
├── 📁 Authentication
│   ├── Register User
│   ├── Login
│   └── Logout
├── 📁 Users
│   ├── List Users
│   ├── Get User by ID
│   ├── Update User
│   └── Delete User
└── 📁 Messages
    ├── Send Message
    ├── List Messages
    └── Delete Message
```

### 3. Add Descriptions

```json
{
  "name": "Login",
  "request": {
    "description": "Authenticate user and receive JWT tokens.\n\nReturns:\n- access: Short-lived token (60 min)\n- refresh: Long-lived token (1 day)\n- user: User profile data",
    "method": "POST",
    ...
  }
}
```

### 4. Always Check Response Status

```javascript
if (pm.response.code === 200) {
    // Success logic
} else {
    console.error('Request failed:', pm.response.text());
}
```

### 5. Log Important Information

```javascript
console.log('User ID:', pm.collectionVariables.get('user_id'));
console.log('Response:', JSON.stringify(pm.response.json(), null, 2));
```

### 6. Use Dynamic Data

**Avoid hardcoded values**:
```json
{"email": "test@example.com"}  ❌
```

**Use variables**:
```json
{"email": "{{test_email}}"}  ✅
```

### 7. Handle Errors Gracefully

```javascript
if (pm.response.code >= 400) {
    console.error('Error:', pm.response.json());
    pm.test('Request succeeded', function() {
        pm.expect.fail('Got error status: ' + pm.response.code);
    });
}
```

### 8. Document Expected Responses

Add example responses:

```json
{
  "name": "Get User",
  "request": { ... },
  "response": [
    {
      "name": "Success Response",
      "originalRequest": { ... },
      "status": "OK",
      "code": 200,
      "_postman_previewlanguage": "json",
      "body": "{\n  \"user_id\": \"abc-123\",\n  \"email\": \"user@example.com\",\n  \"first_name\": \"John\"\n}"
    }
  ]
}
```

### 9. Version Control Your Collection

```bash
# Save to git
git add my_api_collection.json
git commit -m "feat: add user registration endpoint"
git push
```

### 10. Keep It DRY (Don't Repeat Yourself)

Use collection variables instead of repeating values:

**Bad**:
```json
// Request 1
"url": "http://localhost:8000/api/users/"

// Request 2
"url": "http://localhost:8000/api/messages/"
```

**Good**:
```json
// Variable
{"key": "base_url", "value": "http://localhost:8000/api"}

// Request 1
"url": "{{base_url}}/users/"

// Request 2
"url": "{{base_url}}/messages/"
```

---

## Complete Example

Here's a complete, minimal Postman collection:

```json
{
  "info": {
    "_postman_id": "example-collection-001",
    "name": "Simple API Collection",
    "description": "A complete example collection for beginners",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000/api",
      "type": "string"
    },
    {
      "key": "access_token",
      "value": "",
      "type": "string"
    },
    {
      "key": "user_id",
      "value": "",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register User",
          "event": [
            {
              "listen": "prerequest",
              "script": {
                "exec": [
                  "// Generate unique email",
                  "const timestamp = Date.now();",
                  "const email = `user${timestamp}@example.com`;",
                  "pm.collectionVariables.set('test_email', email);"
                ],
                "type": "text/javascript"
              }
            },
            {
              "listen": "test",
              "script": {
                "exec": [
                  "if (pm.response.code === 201) {",
                  "    const response = pm.response.json();",
                  "    pm.collectionVariables.set('access_token', response.access);",
                  "    pm.collectionVariables.set('user_id', response.user.user_id);",
                  "    ",
                  "    pm.test('User registered successfully', function () {",
                  "        pm.expect(response).to.have.property('access');",
                  "        pm.expect(response.user).to.have.property('email');",
                  "    });",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"{{test_email}}\",\n  \"password\": \"SecurePass123!\",\n  \"first_name\": \"Test\",\n  \"last_name\": \"User\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/register/",
              "host": ["{{base_url}}"],
              "path": ["auth", "register", ""]
            },
            "description": "Register a new user and receive authentication tokens"
          },
          "response": []
        },
        {
          "name": "Login",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "if (pm.response.code === 200) {",
                  "    const response = pm.response.json();",
                  "    pm.collectionVariables.set('access_token', response.access);",
                  "    ",
                  "    pm.test('Login successful', function () {",
                  "        pm.expect(response).to.have.property('access');",
                  "        pm.expect(response).to.have.property('user');",
                  "    });",
                  "} else {",
                  "    console.error('Login failed:', pm.response.text());",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"{{test_email}}\",\n  \"password\": \"SecurePass123!\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/login/",
              "host": ["{{base_url}}"],
              "path": ["auth", "login", ""]
            },
            "description": "Authenticate with email and password"
          },
          "response": []
        }
      ],
      "description": "Authentication endpoints"
    },
    {
      "name": "Users",
      "item": [
        {
          "name": "Get Current User",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status code is 200', function () {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test('Response has user data', function () {",
                  "    const response = pm.response.json();",
                  "    pm.expect(response).to.have.property('email');",
                  "    pm.expect(response).to.have.property('user_id');",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/auth/user/",
              "host": ["{{base_url}}"],
              "path": ["auth", "user", ""]
            },
            "description": "Get authenticated user's profile"
          },
          "response": []
        }
      ],
      "description": "User management endpoints"
    }
  ]
}
```

---

## 📝 Quick Reference

### Common Script Commands

```javascript
// Variables
pm.collectionVariables.set('key', 'value');
pm.collectionVariables.get('key');
pm.collectionVariables.unset('key');

// Response
pm.response.code;              // Status code (200, 404, etc.)
pm.response.json();            // Parse JSON response
pm.response.text();            // Get raw text
pm.response.responseTime;      // Time in milliseconds

// Tests
pm.test('Name', function() {
    pm.response.to.have.status(200);
    pm.expect(value).to.equal(expected);
    pm.expect(value).to.be.a('string');
    pm.expect(array).to.include(item);
});

// Logging
console.log('Message');
console.error('Error');
console.warn('Warning');

// Request Info
pm.info.requestName;           // Current request name
pm.request.url.toString();     // Full URL
pm.request.method;             // HTTP method
```

### HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid data |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Not authorized |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Backend problem |

---

## 🎯 Next Steps

1. **Create your first collection** using the template above
2. **Import into Postman** and test it
3. **Add more requests** one at a time
4. **Write tests** for each request
5. **Use variables** to avoid hardcoding
6. **Organize with folders** as collection grows
7. **Version control** with Git
8. **Share with team** for collaboration

---

## 📚 Additional Resources

- [Postman Collection Format](https://schema.postman.com/json/collection/v2.1.0/docs/index.html)
- [Postman Scripting Reference](https://learning.postman.com/docs/writing-scripts/script-references/postman-sandbox-api-reference/)
- [Chai Assertion Library](https://www.chaijs.com/api/bdd/) (used in tests)
- [Newman CLI](https://learning.postman.com/docs/running-collections/using-newman-cli/command-line-integration-with-newman/)

---

**Last Updated**: December 3, 2025  
**Postman Schema Version**: v2.1.0  
**Author**: ALX Backend Python Team
