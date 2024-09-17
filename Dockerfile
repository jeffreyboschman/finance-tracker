# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .
COPY requirements-dev.txt .
COPY pyproject.toml .
COPY src src/

# Install any needed packages specified in requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -e .

# Expose port 7860 for Gradio
EXPOSE 7860

# Run app.py when the container launches
CMD ["python", "src/finance_tracker/gradio-app.py"]