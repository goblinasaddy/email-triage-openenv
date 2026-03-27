FROM python:3.11-slim

WORKDIR /app

ENV PORT=8000

# Copy dependencies list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt google-generativeai python-dotenv

# Copy the rest of the project
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Run the API server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
