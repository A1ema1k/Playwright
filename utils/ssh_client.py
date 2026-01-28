# utils/ssh_client.py — для ISPmanager (проверено по вашему первому рабочему коду)
import asyncssh
import shlex  # ← добавлено
from typing import List, Dict, Any


async def run_ssh_command(
    hostname: str,
    username: str,
    password: str,
    command: str,
    port: int = 22,
    connect_timeout: int = 15,
    command_timeout: int = 30,
) -> Dict[str, Any]:
    try:
        port = int(port)
        print(f"🔌 Подключаюсь к {hostname}:{port} (type={type(port)})")
        async with asyncssh.connect(
            host=hostname,
            port=port,
            username=username,
            password=password,
            known_hosts=None,
            connect_timeout=connect_timeout,
        ) as conn:
            # ✅ Без sh -c — проще и безопаснее для ваших команд
            result = await conn.run(command, timeout=command_timeout)
            return {
                "success": result.exit_status == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip(),
                "exit_code": result.exit_status
            }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "exit_code": -1
        }

async def disable_license_agreement_on_server(server: Dict) -> Dict[str, Any]:
    """Отключает EULA на одном сервере ISPmanager — реалистичный способ"""
    print("🟢 [utils.ssh_client] disable_license_agreement_on_server вызвана")
    hostname = server["hostname"]
    username = server.get("username", "root")
    password = server["password"]
    port = server.get("port", 22)

    result = {
        "hostname": hostname,
        "success": False,
        "steps": {},
        "error": None
    }

    # 1. Проверить, есть ли "Option EULA" в конфиге
    check_cmd = 'grep -q "Option EULA" /usr/local/mgr5/etc/ispmgr.conf && echo "FOUND" || echo "NOT_FOUND"'
    res_check = await run_ssh_command(hostname, username, password, check_cmd, port)
    result["steps"]["check_eula"] = res_check
    if not res_check["success"]:
        result["error"] = f"Ошибка проверки EULA: {res_check['error']}"
        return result

    has_eula = "FOUND" in res_check["output"]
    print(f"  ℹ️ {hostname}: Option EULA {'найден' if has_eula else 'не найден'}")

    # 2. Удалить, если найден
    if has_eula:
        del_cmd = 'sed -i "/Option EULA/d" /usr/local/mgr5/etc/ispmgr.conf'
        res_del = await run_ssh_command(hostname, username, password, del_cmd, port)
        result["steps"]["delete_eula"] = res_del
        if not res_del["success"]:
            result["error"] = f"Ошибка удаления EULA: {res_del['error']}"
            return result
        print(f"  ✅ {hostname}: Option EULA удалён")

    # 3. Перезапустить ispmgr
    restart_ispmgr_cmd = '/usr/local/mgr5/sbin/mgrctl -m ispmgr -R'
    res_restart_ispmgr = await run_ssh_command(hostname, username, password, restart_ispmgr_cmd, port)
    result["steps"]["restart_ispmgr"] = res_restart_ispmgr
    if not res_restart_ispmgr["success"]:
        result["error"] = f"Ошибка перезапуска ispmgr: {res_restart_ispmgr['error']}"
        return result
    print(f"  ✅ {hostname}: ispmgr перезапущен")

    # 4. Перезапустить core
    restart_core_cmd = '/usr/local/mgr5/sbin/mgrctl -m core -R'
    res_restart_core = await run_ssh_command(hostname, username, password, restart_core_cmd, port)
    result["steps"]["restart_core"] = res_restart_core
    if not res_restart_core["success"]:
        result["error"] = f"Ошибка перезапуска core: {res_restart_core['error']}"
        return result
    print(f"  ✅ {hostname}: core перезапущен")

    result["success"] = True
    return result


async def disable_license_agreement_on_servers(servers: List[Dict]) -> Dict[str, Dict]:
    """Групповая версия — для совместимости с test_2fa_workflow.py"""
    results = {}
    for server in servers:
        res = await disable_license_agreement_on_server(server)
        results[server["hostname"]] = res
    return results