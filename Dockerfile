# Используем официальный образ с предустановленным браузером и зависимостями
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# Запускаем тесты (замените на вашу команду)
CMD ["python", "-m", "pytest", "-v"]