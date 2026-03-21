FROM python:3.13-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the sentence-transformers model so first request is fast
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2')"

# Copy the entire project
COPY . .

# Expose port (7860 = HF Spaces default, also works on Render/Railway via PORT env)
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Run the server from the Backend directory
WORKDIR /app/Backend
CMD ["python", "server.py"]
