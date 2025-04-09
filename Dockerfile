# Use a lightweight version of python as the base
FROM python:3.13-alpine

# Set the working directory for the docker container
WORKDIR /code

# Copy the requirements.txt and install it
## this is done separately so we it runs as a separate layer (better for caching)
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 3000

# Copy everything else
COPY . .

# Run the fast api server
WORKDIR /code/src
CMD ["fastapi", "run", "server.py", "--port", "3000"]