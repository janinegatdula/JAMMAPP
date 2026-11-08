# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run Streamlit on port 8080 (Cloud Run requires this)
CMD ["streamlit", "run", "App.py", "--server.port=8080", "--server.address=0.0.0.0"]
