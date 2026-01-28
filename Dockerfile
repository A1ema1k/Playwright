cd /tmp
git clone https://github.com/A1ema1k/Playwright.git
cd Playwright

# Создаём минимальный Dockerfile если его нет
cat > Dockerfile << 'EOF'
FROM mcr.microsoft.com/playwright/python:v1.40.0-focal
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-m", "pytest"]
EOF

# Собираем из локальной папки
docker build -t playwright-tests:latest .