# Python Image
FROM python:3.9-slim

# System Dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    wget \
    unzip \
    curl \
    gnupg \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Chrome
RUN curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ChromeDriver
RUN wget -q -O /tmp/chromedriver.zip  https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.182/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip

# Vars for chrome
ENV DISPLAY=:99

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# move script
COPY fetch_schedules.py /usr/src/app/

WORKDIR /usr/src/app

# Entrypoint
ENTRYPOINT ["python", "fetch_schedules.py"]