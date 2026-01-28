# Используем официальный образ Playwright для Python (Ubuntu 22.04)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Копируем зависимости и устанавливаем пакеты
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Запускаем конкретный тест (безоконный режим включён по умолчанию в образе)
CMD ["python", "-m", "pytest", "tests/test_2fa/test_2fa_workflow.py", "-v"]