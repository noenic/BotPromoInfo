# Use Python as the base image
FROM python:3.11-alpine3.18

# Set the working directory
WORKDIR /app

# Copy the current directory into the container at /app
COPY . /app

# Install the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Specify the command to run when the container starts
CMD [ "python3","-u","HegoBot.py" ]
