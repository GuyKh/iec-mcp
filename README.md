# IEC API MCP Server

This project provides a Model Context Protocol (MCP) server for interacting with the Israel Electric Corporation (IEC) API. It exposes various functionalities of the `iec-api` Python library as MCP tools, allowing for programmatic access and integration with other systems.

## Project Goal
The primary goal is to simplify interaction with the `iec-api` by abstracting its complexities behind a standardized MCP interface. This enables automation, improves interoperability, and enhances the developer experience for agents and applications needing to access IEC data.

## Features
- **Authentication:** Supports OTP-based login and loading of existing JWT tokens.
- **Data Retrieval:** Access to customer data, accounts, contracts, meter readings, electric bills, devices, and more.
- **Static Data:** Retrieve various tariffs (kWh, distribution, delivery, KVA) and usage calculator information.
- **Masa API Integration:** Tools for interacting with Masa API endpoints, including equipment, user profiles, cities, order categories, volt levels, order titles, and lookup data.
- **Fault Portal Integration:** Access to user profiles and outage information from the Fault Portal.

## Setup and Installation

1.  **Clone the repository:**
    If you haven't already, clone this repository to your local machine.

2.  **Navigate to the project directory:**
    ```bash
    cd iec-mcp
    ```

3.  **Set up a Python virtual environment and install dependencies using `uv`:**
    ```bash
    uv sync
    ```

## Running the Server

You have two options to run the server: using a Python virtual environment or using Docker.

### Option 1: Using uv

1.  **Run the MCP server:**
    ```bash
    uv run python main.py
    ```
    The server will start and be ready to accept MCP connections. Keep this terminal running.

### Option 2: Using a Python Virtual Environment

1.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate
    ```

2.  **Run the MCP server:**
    ```bash
    python main.py
    ```
    The server will start and be ready to accept MCP connections. Keep this terminal running.

### Option 3: Running with Docker

1.  **Build the Docker image:**
    ```bash
    docker build -t iec-api-mcp .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 8000:8000 iec-api-mcp
    ```
    The server will be accessible at `http://localhost:8000`.

## Using the MCP Tools

Once the server is running, you can interact with it using MCP clients. The OpenAPI documentation, which lists all available tools and their schemas, can be accessed at `http://localhost:8000/docs` in your web browser.

### Authentication

Before using most data retrieval tools, you need to authenticate. You have two options:

#### Option 1: Initiate OTP Login Flow (Recommended for first-time login)

1.  **Initiate Login with your Israeli ID (SSN):**
    In a **new terminal** (or a separate process if the server is running in the background), use the `use_mcp_tool` command to call the `login_with_id` tool. Replace `YOUR_ISRAELI_ID` with your actual Israeli ID (SSN):
    ```xml
    <use_mcp_tool>
    <server_name>http://localhost:8000</server_name>
    <tool_name>login_with_id</tool_name>
    <arguments>
    {
      "user_id": "YOUR_ISRAELI_ID"
    }
    </arguments>
    </use_mcp_tool>
    ```
    After executing this, you should receive a One-Time Password (OTP) on your registered device.

2.  **Verify OTP:**
    Once you receive the OTP, use the `verify_otp` tool in the same manner, replacing `YOUR_OTP_CODE` with the code you received:
    ```xml
    <use_mcp_tool>
    <server_name>http://localhost:8000</server_name>
    <tool_name>verify_otp</tool_name>
    <arguments>
    {
      "otp_code": "YOUR_OTP_CODE"
    }
    </arguments>
    </use_mcp_tool>
    ```
    Upon successful verification, the MCP server will be authenticated.

#### Option 2: Load an Existing JWT Token

If you have a previously saved JWT token, you can load it directly to authenticate. Replace the placeholder values with your actual token details:
```xml
<use_mcp_tool>
<server_name>http://localhost:8000</server_name>
<tool_name>load_jwt_token</tool_name>
<arguments>
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "refresh_token": "YOUR_REFRESH_TOKEN",
  "token_type": "YOUR_TOKEN_TYPE",
  "expires_in": 3600,
  "scope": "YOUR_SCOPE",
  "id_token": "YOUR_ID_TOKEN"
}
</arguments>
</use_mcp_tool>
```

### Example Tool Usage (after authentication)

Once authenticated, you can call other tools. For example, to get customer data:
```xml
<use_mcp_tool>
<server_name>http://localhost:8000</server_name>
<tool_name>get_customer</tool_name>
<arguments>{}</arguments>
</use_mcp_tool>
```

## Development and Contribution
Refer to the `memory-bank/` directory for detailed project context, system patterns, and technical considerations.
