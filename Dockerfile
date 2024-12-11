FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the Flask port
EXPOSE 5000

# Start the Flask server
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
