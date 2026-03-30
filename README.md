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

This path should lead to the repos folder that contains your repos and files you intend to analyze. The files will be available inside the container under `app/repos/` directory

Use the format provided in the `.env.example` file as a template.

**Note**: For instructions on using developer provided test files see 'Test file configuration and usage' section below

Another environment variable you should set up is the API key for the online LLM. Set it up as such: `OPENROUTER_API_KEY=sk-....`

The overall content of the .env file should be:

```
REPOS_PATH="somepath"
OPENROUTER_API_KEY=sk-....
```

#### Test file configuration and usage

- A snapshot of all of our test files are included in the repo under `utils/test_projects` along with detailed explanations and usage instruction in our [Test file documentation](utils\test_projects\test_projects_documentation.md).

- For more options and up-to-date files, you can also download our test files from this [Public Google Drive folder]( https://drive.google.com/drive/folders/1eEMyr1wQC3RZCKBvMEIblr8b4RKu4Tv5?usp=drive_link)

- In brief, the test files will be automatically available inside the backend/CLI container at `app/test_projects`. Alternatively you can copy the test files from the repo to the path specified in your `.env`

- For the Webapp GUI upload the test files directly from the repo like you would any other file.

---

### 3. Build and Run the Docker Container

From the `app` directory, build and start the container:

```bash
docker compose up -d --build
```

This command will build the container in detached mode.

**Important Note**: If you have built the app before on your system ensure that all related volumes are deleted before compose command. Stale volumes will cause database scripts to fail!

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

- If you wish to test project ranking features and other user interactions:
  - Enter: `/app/test_projects/multiple_projects` 

- If you wish to test incremental analysis:  
  - First enter: `/app/test_projects/capstone_snapshot_feb7.zip`
  - Then when updating analysis: `/app/test_projects/capstone_updated_snapshot_feb14.zip`

- If you wish to analyze your own files, Enter : `/app/repos/<yourFileZipOrDirectory>` or `/app/repos/` to analyze all of your files together

**Note:** The files are accessible at this path because they were volume-mounted into the container during the Docker build process.

### 7. Interact with the System

Follow the on-screen prompts to:

- Test the system's functionality
- Run analysis on uploaded files
- Explore different features
- When prompted to enter git username:
  - Enter: sitharachari
- When prompted to enter associated email: 
  - Enter: sithara12.chari@gmail.com

---

## System API:

For an indepth understanding of the API endpoints for this system, please [view our API Documentation here](docs/plan/API%20Documentation.md)

---
## Testing Report

The project includes a comprehensive test suite covering frontend components, backend API endpoints, file processing, text analysis, LLM integration, portfolio/resume generation, and database operations.

Frontend tests use **Vitest + React Testing Library**, and backend tests use **Pytest** with a dedicated PostgreSQL `test_db` for integration and end-to-end testing.

[View the full Testing Report here](docs/plan/Testing%20Report.md)

---
## Known Bugs and Future Suggestions

All currently known bugs have been documented alongside a list of plans for future improvements to our system. If you encounter any bugs that have not been documented please feel free to reach out! 

[View the full list of known bugs and future suggestions here](docs/plan/Known%20Bugs.md)

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
