# **PhoneGetter API Documentation**

PhoneGetter API is a closed API created solely to facilitate communication between devices and the server. It is 
designed to manage device registration, update cell data, and handle user interactions securely through an API token 
for authentication. All requests, except for device creation, require an authentication token to ensure secure and 
authorized communication.

#### **Base URL:**
`https://phonegetter.onrender.com/api`

---

## **Authentication**

All requests except `/create_device` require authentication using an API token. The token must be passed in the `Authorization` header as follows:

```
Authorization: <token>
```

If your token contains special characters, such as `$`, that may be not interpreted by the shell. For example you can use "\" before "$"":

```
Authorization: pbkdf2:sha256:600000\$xHE71eVNhO0jUC8B\$d0e7148c912c353b12ca831f18e6e9b59f639ff319319ae5dae5ed3fa85cc985
```

---

## API Endpoints

### **1. Create Device**
- **Endpoint:** `/create_device`
- **Method:** `POST`
- **Description:** Creates a new device and generates a unique API token for it.
  - **_Note: This endpoint is intended for development purposes only. In the finished product, this endpoint should be closed to regular users._**
- **Request Body:**
  ```json
  {
    "name": string,  // The name of the device
    "ip": string     // The unique IP address of the device
  }
  ```
- **Response:**
  ```json
  {
    "status": "success" or "error",   // The operation status
    "token": string                   // The generated API token for the device
  }
  ```
- **HTTP Status Codes:**
  - `201`: Device created successfully.
  - `400`: Device with that IP address already exists.
  
- **Example Request:**
  ```bash
  curl -X POST https://phonegetter.onrender.com/api/create_device \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Class 255",
    "ip": "255.255.255.255"
  }'
  ```
- **Example Response:**
  ```json
  {
    "status": "success",
    "token": "pbkdf2:sha256:600000$xHE71eVNhO0jUC8B$d0e7148c912c353b12ca831f18e6e9b59f639ff319319ae5dae5ed3fa85cc985"
  }
  ```

---

### **2. Reset Connection**
- **Endpoint:** `/reset_connection`
- **Method:** `GET`
- **Description:** Removes the connection between the device and its owner. Requires a valid API token.
- **Request Body:** Not required.
- **Response:**
  ```json
  {
    "status": "success" or "error",   // The operation status
    "device": string     // The name of the device
  }
  ```
- **HTTP Status Code:**
  - `200`: Connection successfully removed.
  - `403`: Missing or invalid API token.

- **Example Request:**
  ```bash
  curl -X GET https://phonegetter.onrender.com/api/reset_connection \
  -H "Authorization: pbkdf2:sha256:600000\$xHE71eVNhO0jUC8B\$d0e7148c912c353b12ca831f18e6e9b59f639ff319319ae5dae5ed3fa85cc985"
  ```

- **Example Response:**
  ```json
  {
    "status": "success",
    "device": "Class 255"
  }
  ```

---

### **3. Update Data**
- **Endpoint:** `/update_data`
- **Method:** `PUT`
- **Description:** Updates the device's cell data and tracks changes in the user's phone history. Requires a valid API token.
- **Request Body:**
  ```json
  {
    "changed_cell": int,   // The identifier of the cell that was updated
    "state": bool          // The new state of the cell
  }
  ```
- **Response:**
  ```json
  {
    "status": "success" or "error",   // The operation status
    "device": string                  // The name of the device
  }
  ```
- **HTTP Status Codes:**
  - `200`: Data successfully updated.
  - `400`: Invalid data for 'changed_cell'.
  - `403`: Missing or invalid API token.
  - `404`: User not found.
  
- **Example Request:**
  ```bash
  curl -X PUT https://phonegetter.onrender.com/api/update_data \
    -H "Content-Type: application/json" \
    -H "Authorization: pbkdf2:sha256:600000\$86La8ZLiYC0fyueH\$858727d0608b50906633a9d3a692d597016a0f9cddfb19ffece4fb2d66aafd03" \
    -d '{
      "changed_cell": 1,
      "state": true
    }'
  ```
- **Example Response:**
  ```json
  {
    "status": "success",
    "device": "Class 255"
  }
  ```

---

### **4. Give Data**
- **Endpoint:** `/give_data`
- **Method:** `GET`
- **Description:** Returns the device's data about the state of cells. Requires a valid API token.
- **Response:**
  ```json
  {
    "status": "success" or "error",   // The operation status
    "device": string,                 // The name of the device
    "cells": {                        // Data about the cell's state
      "cell_id": [user_id, state],
      ...
    }
  }
  ```
- **HTTP Status Code:**
  - `200`: Data successfully returned.
  - `403`: Missing or invalid API token.

- **Example Request:**
  ```bash
  curl -X GET https://phonegetter.onrender.com/api/give_data \
  -H "Authorization: pbkdf2:sha256:600000\$xHE71eVNhO0jUC8B\$d0e7148c912c353b12ca831f18e6e9b59f639ff319319ae5dae5ed3fa85cc985"
  ```

- **Example Response:**
  ```json
  {
    "status": "success",
    "device": "Class 255",
    "cells": {
      "1": [1, true],
      "2": [2, false]
    }
  }
  ```

---

### **5. Create Code**
- **Endpoint:** `/create_code`
- **Method:** `GET`
- **Description:** Generates and returns a secret token for device registration. Requires a valid API token.
- **Response:**
  ```json
  {
    "status": "success" or "error",   // The operation status
    "device": string,                 // The name of the device
    "token": int                      // The secret token for registration
  }
  ```
- **HTTP Status Code:**
  - `200`: Token successfully generated.
  - `403`: Missing or invalid API token.

- **Example Request:**
  ```bash
  curl -X GET https://phonegetter.onrender.com/api/create_code \
  -H "Authorization: pbkdf2:sha256:600000\$xHE71eVNhO0jUC8B\$d0e7148c912c353b12ca831f18e6e9b59f639ff319319ae5dae5ed3fa85cc985"
  ```

- **Example Response:**
  ```json
  {
    "status": "success",
    "device": "Class 255",
    "token": 1234567
  }
  ```