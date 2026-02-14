Dockerization and Deployment Plan
Goal Description
Containerize the application using Docker to enable easy deployment to cloud platforms like Render or Railway. The goal is to have a single Docker image that runs both the FastAPI backend and provides the React frontend.

Proposed Changes
Configuration
[NEW] 
Dockerfile
Multi-stage build:
Build Stage: Node.js image to build the React frontend (npm run build).
Runtime Stage: Python image to install backend dependencies and serve the app.
Copy built frontend assets to the backend container.
[NEW] 
.dockerignore
Exclude node_modules, venv, __pycache__, and data files to keep the image small and secure.
Backend
[MODIFY] 
backend/main.py
Mount the frontend/dist directory as a static file path.
Add a "catch-all" route to serve 
index.html
 for client-side routing (so direct links to /chat work).
Documentation
[NEW] 
deployment.md
Step-by-step specific instructions for deploying to Render (easiest free tier).
Instructions for running locally with Docker.
Verification Plan
Automated Tests
None.
Manual Verification
Build the Docker image locally: docker build -t companion .
Run the container: docker run -p 8000:8000 companion
Verify the app loads at http://localhost:8000 (Frontend served by Backend).
Verify API works and persistence still happens (in the container).