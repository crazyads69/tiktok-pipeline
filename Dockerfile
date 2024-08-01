FROM python:3.10-slim

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdbus-1-3 libdrm2 libxcb1 libxkbcommon0 libatspi2.0-0 libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2

# Reinstall the TikTok API
RUN pip install TikTokApi
RUN python -m playwright install

# Copy the src code into the container
COPY ./src .

# Copy the .env file into the container
COPY .env .

# Run the script
CMD ["python", "crawl_data.py"]