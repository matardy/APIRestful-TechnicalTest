# API Documentation

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [User Registration](#user-registration)
  - [User Login](#user-login)
  - [Store Sensitive Data](#store-sensitive-data)
  - [Retrieve Sensitive Data](#retrieve-sensitive-data)
  - [Update Credentials](#update-credentials)
  - [Upload Profile Picture](#upload-profile-picture)
  - [Get Profile Picture](#get-profile-picture)
- [AWS Integration](#aws-integration)
  - [S3 Bucket](#s3-bucket)

---

## Introduction

This document describes the API and its endpoints, including authentication and integration with AWS services like S3.

## Prerequisites

- AWS keys are needed and are stored in a `.env` file.
- Docker is used for development. Run `docker-compose up` to start the application.

## Authentication

JWT is used for authentication. The token should be included in the `Authorization` header with the format `Bearer {Your-Token}`.

---

## Endpoints

### User Registration

- **Endpoint**: `POST /register`
- **Response Type**: JSON

#### Request Body

- `username`: String
- `password`: String

#### Response

- 201 Created
- 400 Username already exists

---

### User Login

- **Endpoint**: `POST /login`
- **Response Type**: JSON

#### Request Body

- `username`: String
- `password`: String

#### Response

- 200 OK
- 401 Unauthorized

---

### Store Sensitive Data

- **Endpoint**: `POST /store-sensitive-data`
- **Response Type**: JSON

#### Headers

- `Authorization`: Bearer Token

#### Request Body

- `credit_card_number`: String

#### Response

- 200 OK
- 401 Unauthorized

---

### Retrieve Sensitive Data

- **Endpoint**: `GET /retrieve-sensitive-data`
- **Response Type**: JSON

#### Headers

- `Authorization`: Bearer Token
- `Unique-Token`: Unique token generated when storing sensitive data

#### Response

- 200 OK
- 401 Unauthorized
- 404 Data Not Found

---

### Update Credentials

- **Endpoint**: `PUT /update-credentials`
- **Response Type**: JSON

#### Headers

- `Authorization`: Bearer Token

#### Request Body

- `current_password`: String
- `new_username`: String (Optional)
- `new_password`: String (Optional)

#### Response

- 200 OK
- 401 Unauthorized

---

### Upload Profile Picture

- **Endpoint**: `POST /upload-profile-picture`
- **Response Type**: JSON

#### Headers

- `Authorization`: Bearer Token

#### Request Body

- `file`: File

#### Response

- 200 OK
- 500 Internal Server Error

---

### Get Profile Picture

- **Endpoint**: `GET /get-profile-picture`
- **Response Type**: JSON

#### Headers

- `Authorization`: Bearer Token

#### Response

- 200 OK
- 500 Internal Server Error

---

## AWS Integration

### S3 Bucket

- Bucket Name: `profile-pictures-techtest`
- AWS keys are needed for S3 and are loaded from a `.env` file.
