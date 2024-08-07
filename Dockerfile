# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim

# Set our working directory to the CropGen root folder.
WORKDIR /crop-gen

# Expose port(s)
EXPOSE 27746

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Copy the requirements text file and ask pip to install of our packages for us.
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all of our app files (see .dockerignore for files/directories that should be ignored)
COPY . .

# Setup environment variables
ENV RUNNING_IN_CONTAINER Yes

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "main.py"]
