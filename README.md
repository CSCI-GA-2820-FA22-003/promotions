# NYU DevOps Promotions

[![Build Status](https://github.com/nyudevops-promotions/promotions/actions/workflows/ci.yml/badge.svg)](https://github.com/nyudevops-promotions/promotions/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA22-003/promotions/branch/main/graph/badge.svg?token=7QW1Z8EFFN)](https://codecov.io/gh/CSCI-GA-2820-FA22-003/promotions)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Overview

This repository contains code for the Promotions service. The promotions resource is a representation of a special promotion or sale that is running against a product or perhaps the entire store. Some examples are "buy 1 get 1 free", "20% off", etc. Discount promotions usually apply for a given duration (e.g., sale for 1 week only). 

## Setup Promotion Service

To run the service please follow the steps:

- Git clone the repository on your local

    `git clone https://github.com/CSCI-GA-2820-FA22-003/promotions.git`

- Start your service using the following command

    `Honcho start`

- Use the following command to run any Unit Tests available for the repo

    `nosetests`

## Contents

The repository is structured in the below manner:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## Promotion APIs

The following segment details out the Promotion Service's CRUD APIs with sample URLs, Request Body, and Responses. 

### GET /promotions/[id]

Example: `GET http://localhost:8000/promotions/007`

Response body:

    {
        "created_at": "2009-01-01",
        "description": "Test Description",
        "expiry": "2009-01-03",
        "id": 007,
        "last_updated_at": "2009-01-02",
        "name": "Test Promotion for Get",
        "promotion_percent": 0.42,
        "promotion_value": 69,
        "status": true,
        "type": "ABS_DISCOUNT"
    }


### POST /promotions

Example: `Create – POST  http://localhost:8000/promotions`

Request body:

    {
        "name": "Test Promotion for Get",
        "type": "ABS_DISCOUNT",
        "description": "Test Description",
        "promotion_value": 69,
        "promotion_percent": 0.42,
        "status": true,
        "expiry": "2009-01-03",
        "created_at": "2009-01-01",
        "last_updated_at": "2009-01-02"
    }

Response body:

    {
        "created_at": "2009-01-01",
        "description": "Test Description",
        "expiry": "2009-01-03",
        "id": 007,
        "last_updated_at": "2009-01-02",
        "name": "Test Promotion for Get",
        "promotion_percent": 0.42,
        "promotion_value": 69,
        "status": true,
        "type": "ABS_DISCOUNT"
    }


### PUT /promotions/[id]

Example: `Update – PUT  http://localhost:8000/promotions/007`

Request body:

    {
        "name": "Test Promotion for Get",
        "type": "ABS_DISCOUNT",
        "description": "Test Description - Updating",
        "promotion_value": 71,
        "promotion_percent": 0.43,
        "status": false,
        "expiry": "2009-01-03",
        "created_at": "2009-01-01",
        "last_updated_at": "2009-01-02"
    }

Response body:

    {
        "created_at": "2009-01-01",
        "description": "Test Description - Updating",
        "expiry": "2009-01-03",
        "id": 007,
        "last_updated_at": "2009-01-02",
        "name": "Test Promotion for Get - 2",
        "promotion_percent": 0.43,
        "promotion_value": 71,
        "status": false,
        "type": "ABS_DISCOUNT"
    }


### DELETE /promotions/[id]

Example: `DELETE  http://localhost:8000/promotions/007`


## License

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
