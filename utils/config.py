# utils/config.py
# Конфигурация для эталонной (REFERENCE) и тестируемой (TEST) панелей

# URL для тестов
REFERENCE_URL = "https://172.31.97.121:1500/"
REFERENCE_USERNAME = "root"
REFERENCE_PASSWORD = "Patrick23"

TEST_URL = "https://172.31.97.122:1500/"
TEST_USERNAME = "root"
TEST_PASSWORD = "Patrick23"

# SSH настройки для подготовки серверов
REFERENCE_SERVER = {
    'hostname': '172.31.97.121',
    'username': 'root',
    'password': 'Patrick23',
    'port': 22
}

TEST_SERVER = {
    'hostname': '172.31.97.122',
    'username': 'root',
    'password': 'Patrick23',
    'port': 22
}

# Список всех серверов для подготовки
ALL_SERVERS = [REFERENCE_SERVER, TEST_SERVER]