# Capstone Project Setup Instructions

Welcome! This guide will walk you through setting up and running our capstone project for grading. Please follow these steps carefully.

---

## Prerequisites

- Docker installed and running
- Visual Studio Code with Docker extension
- Git for cloning the repository

### Important for Mac Users

If you're using a Mac, you'll need to adjust Docker's resource allocation:

1. Open **Docker Desktop**
2. Click the **settings icon** in the top right corner
3. Navigate to **Resources**
4. Set **"Memory Limit"** to the maximum GB amount available
5. Set **"Swap"** to **2 GB**
6. Click **"Apply & Restart"**

---

## Setup Steps

### 1. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone https://github.com/COSC-499-W2025/capstone-project-team-12.git
```

Open the project in Visual Studio Code.

### 2. Configure Environment Variables

In the VS Code terminal, navigate to the `app` directory:

```bash
cd app
```

Create a new file named `.env` at the app level, then copy the contents from `.env.example`:

```bash
cp .env.example .env
```

**Important:** Open the `.env` file and specify the file paths to access your:
- Repositories
- Nested files
- Zip files
- Documents

Use the format provided in the `.env.example` file as a template.

### 3. Build and Run the Docker Container

From the `app` directory, build and start the container:

```bash
docker compose up -d --build
```

This command will build the container in detached mode.

### 4. Attach to the Container

1. In Visual Studio Code, click on the **Docker/Containers icon** on the left sidebar
2. Locate the `app-backend_app` container
3. **Right-click** on the container
4. Select **"Attach Visual Studio Code"**

This will open a new VS Code window connected to the container's file system.

### 5. Run the Backend Pipeline

In the attached container's terminal, execute:

```bash
python main.py
```

### 6. Select File Path for Analysis

When prompted to select the file path:

- Enter: `/app/repos`
- Or copy the `repos` folder path

**Note:** The files are accessible at this path because they were volume-mounted into the container during the Docker build process.

### 7. Interact with the System

Follow the on-screen prompts to:
- Test the system's functionality
- Run analysis on uploaded files
- Explore different features

---

## Troubleshooting

If you encounter any issues:

- Ensure Docker is running and has sufficient resources
- Verify that all file paths in `.env` are correct
- Check that the container built successfully without errors
- Make sure you're in the correct directory when running commands

---

## Thank You!

Thank you for taking the time to review and grade our project. We hope the setup process is smooth and straightforward.

**Happy Holidays!** 🎄

---

*For questions or issues, please don't hesitate to reach out.*

--- 
<br>


## Work Breakdown Diagram

[Work Breakdown Structure (Text Format)](https://github.com/COSC-499-W2025/capstone-project-team-12/blob/project-plans/docs/plan/Work%20Breakdown%20Diagram%20Description.md)

<img width="4900" height="2223" alt="CAPSTONE WBS" src="https://github.com/user-attachments/assets/41aed394-48b3-48e6-812c-97253b352b92" />

## Data Flow Diagrams

[Link to DFD Level 0 Image Only](https://github.com/COSC-499-W2025/capstone-project-team-12/blob/1f6f109c44c3f30c8d1d35acdc7efaa5253d45c2/docs/plan/imgs/Level%200%20DFD.png)

[Link to DFD Level 1 Image Only](https://github.com/COSC-499-W2025/capstone-project-team-12/blob/1f6f109c44c3f30c8d1d35acdc7efaa5253d45c2/docs/plan/imgs/Level%201%20DFD.png)

[Link to DFD Level 1 with Explanation](https://github.com/COSC-499-W2025/capstone-project-team-12/blob/111b27dc38ba19d7a0e577bf896a2e2534fdf8e5/docs/plan/DFD%20Level%201%20Explanation.md)

## System Architecture Diagram

[Link to System Architecture Diagram Image Only](https://github.com/COSC-499-W2025/capstone-project-team-12/blob/517f7f8ecb11361e6318d01da7bbaefc2c26a7de/docs/plan/imgs/System%20Architecture%20Diagram.png)

[Link to System Architecture Diagram with Explanation](https://github.com/COSC-499-W2025/capstone-project-team-12/blob/111b27dc38ba19d7a0e577bf896a2e2534fdf8e5/docs/plan/System%20Architecture%20Diagram%20Explanation.md)

## Project Proposal
[Link to Project Proposal](https://github.com/COSC-499-W2025/capstone-project-team-12/blob/c240296205b4e40998d494888c9242e36341b1ce/docs/plan/Group%2012%20Project%20Proposal.md)

## Team Contract
[Link to Team Contract](https://github.com/COSC-499-W2025/capstone-project-team-12/blob/update-readme/docs/plan/Team%20Contract.md)
