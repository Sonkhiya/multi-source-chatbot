# Multi-Source Chatbot

This repository contains the source code for a multi-source chatbot application.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8+
- `pip`
- Docker
- Docker Compose
- `make`

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd multi-source-chatbot
```

### 2. Install Dependencies

To install the required Python packages, run:

```bash
make install
```

This will install all dependencies listed in `requirements.txt`.

## Usage

### Development Mode

To run the application in development mode with live reloading, use:

```bash
make dev
```

The application will be available at `http://0.0.0.0:8000`.

### Docker

To build and run the application using Docker, follow these steps:

1.  **Build the Docker image:**
    ```bash
    make docker-build
    ```

2.  **Start the services in detached mode:**
    ```bash
    make docker-up
    ```

3.  **View container logs:**
    ```bash
    make docker-logs
    ```

4.  **Stop and remove the containers:**
    ```bash
    make docker-down
    ```

## Available Commands

Here is a list of all available `make` commands for managing the application:

*   `make install`: Install dependencies.
*   `make dev`: Run in development mode.
*   `make test`: Run tests.
*   `make docker-build`: Build Docker image.
*   `make docker-up`: Start Docker containers.
*   `make docker-down`: Stop Docker containers.
*   `make docker-logs`: View Docker logs for the chatbot service.
*   `make clean`: Clean cache and build files.
*   `make logs`: View application logs from `logs/chatbot.log`.