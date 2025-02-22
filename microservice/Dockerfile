# Dockerfile for Mock Microservice

FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the microservice will run on
EXPOSE 3000

# Command to run the microservice (ensure app.py exists and is your entrypoint)
CMD ["python", "app.py"]
