# pages/license_agreement_page/ssh_management.py
import asyncio
from typing import List, Dict
from utils.ssh_client import disable_license_agreement_on_servers


async def disable_license_agreement_on_server(server: Dict) -> Dict:
    """
    Отключает лицензионное соглашение на одном сервере
    """
    result = {
        'hostname': server['hostname'],
        'success': False,
        'actions': []
    }

    ssh = SSHClient(
        hostname=server['hostname'],
        username=server['username'],
        password=server['password'],
        port=server.get('port', 22)
    )

    try:
        # Подключаемся
        if not await ssh.connect():
            result['error'] = "Не удалось подключиться по SSH"
            return result

        # 1. Проверяем наличие Option EULA
        success, output, error = await ssh.execute_command(
            'grep "Option EULA" /usr/local/mgr5/etc/ispmgr.conf || echo "NOT_FOUND"'
        )

        if success and output != "NOT_FOUND":
            result['actions'].append("Option EULA найден")
            print(f"  📝 {server['hostname']}: Option EULA найден, удаляем...")

            # 2. Удаляем строку
            success, output, error = await ssh.execute_command(
                'sed -i "/Option EULA/d" /usr/local/mgr5/etc/ispmgr.conf'
            )

            if success:
                result['actions'].append("Option EULA удален")
                print(f"  ✅ {server['hostname']}: Option EULA удален")
            else:
                result['error'] = f"Ошибка удаления: {error}"
                return result
        else:
            result['actions'].append("Option EULA не найден")
            print(f"  ℹ️ {server['hostname']}: Option EULA не найден")

        # 3. Перезагружаем ispmgr
        print(f"  🔄 {server['hostname']}: Перезагружаем ispmgr...")
        success, output, error = await ssh.execute_command('/usr/local/mgr5/sbin/mgrctl -m ispmgr -R')

        if success:
            result['actions'].append("ispmgr перезагружен")
            print(f"  ✅ {server['hostname']}: ispmgr перезагружен")
        else:
            result['error'] = f"Ошибка перезагрузки ispmgr: {error}"
            return result

        # 4. Перезагружаем core
        print(f"  🔄 {server['hostname']}: Перезагружаем core...")
        success, output, error = await ssh.execute_command('/usr/local/mgr5/sbin/mgrctl -m core -R')

        if success:
            result['actions'].append("core перезагружен")
            print(f"  ✅ {server['hostname']}: core перезагружен")
        else:
            result['error'] = f"Ошибка перезагрузки core: {error}"
            return result

        result['success'] = True
        return result

    except Exception as e:
        result['error'] = f"Исключение: {e}"
        return result
    finally:
        await ssh.close()


async def disable_license_agreement_on_servers(servers: List[Dict]) -> Dict:
    """
    Отключает лицензионное соглашение на всех указанных серверах
    """
    print("🔴 [ssh_management] disable_license_agreement_on_server вызвана")
    print("🚀 Отключаем лицензионное соглашение на серверах...")

    results = {}
    tasks = []

    # Запускаем параллельно для всех серверов
    for server in servers:
        task = disable_license_agreement_on_server(server)
        tasks.append(task)

    # Ждем завершения всех задач
    server_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Обрабатываем результаты
    for result in server_results:
        if isinstance(result, Exception):
            results[result['hostname']] = {'success': False, 'error': str(result)}
        else:
            results[result['hostname']] = result

    return results


async def wait_for_panel_restart(seconds: int = 5):
    """Ожидание после перезагрузки панели"""
    print(f"⏳ Ждем {seconds} секунд после перезагрузки панели...")
    await asyncio.sleep(seconds)
    print("✅ Панели готовы к тестам")