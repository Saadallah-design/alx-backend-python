# 0x03. Unittests and Integration Tests

## Description
This project focuses on writing unit tests and integration tests for Python applications. It covers testing utility functions, memoization, and HTTP client interactions using unittest framework with parameterized tests and mocking.

## Learning Objectives
- Understand the difference between unit and integration tests
- Use common testing patterns such as mocking, parametrizations, and fixtures
- Write effective unit tests for functions and classes
- Test HTTP requests and responses using mocks
- Implement parameterized tests to reduce code duplication

## Requirements
- All files will be interpreted/compiled on Ubuntu 18.04 LTS using python3 (version 3.7)
- All files should end with a new line
- The first line of all files should be exactly `#!/usr/bin/env python3`
- A `README.md` file, at the root of the folder of the project, is mandatory
- Code should use the `pycodestyle` style (version 2.5)
- All files must be executable
- All modules should have documentation
- All classes should have documentation
- All functions (inside and outside a class) should have documentation
- A documentation is not a simple word, it's a real sentence explaining the purpose of the module, class or method
- All functions and coroutines must be type-annotated

## Files
- `utils.py` - Contains utility functions for accessing nested maps, fetching JSON from URLs, and memoization decorator
- `test_utils.py` - Unit tests for utility functions

## Usage
Run tests using unittest:
```bash
python3 -m unittest test_utils.py
```

Run specific test class:
```bash
python3 -m unittest test_utils.TestAccessNestedMap
```

## Author
ALX Backend Python - Week 4 Unit Testing Project
