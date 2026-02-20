import argparse
import telnetlib
import os
import sys
import time

# Данные для подключения из переменных окружения
ADDR = os.getenv("ES_ADDR")
USER = os.getenv("ES_USER")
PASS = os.getenv("ES_PASS")

class ZelaxSwitch:
    def __init__(self, host, login, pwd):
        self.host = host
        self.login = login
        self.pwd = pwd
        self.tn = None

    def connect(self):
        try:
            # Таймаут 10 сек, на всякий случай, если линк плохой
            self.tn = telnetlib.Telnet(self.host, timeout=10)
            
            # Ждем приглашение на логин
            self.tn.read_until(b"Username:", timeout=5)
            self.tn.write(self.login.encode('ascii') + b"\n")
            
            # Вводим пароль
            self.tn.read_until(b"Password:", timeout=5)
            self.tn.write(self.pwd.encode('ascii') + b"\n")
            
            # Переходим в привилегированный режим
            time.sleep(1)
            self.tn.write(b"enable\n") 
            return True
        except Exception as e:
            print(f"Ошибка подключения к {self.host}: {e}")
            return False

    def push_config(self, cmds):
        """Применение конфигурации"""
        if not self.connect():
            return
        
        # Стандартная процедура: вход в config, конфинурация, сохранение
        full_script = ["configure terminal"] + cmds + ["end", "write memory", "exit"]
        
        for line in full_script:
            # Отправка команд в коммутатор
            self.tn.write(line.encode('ascii') + b"\n")
            # Ждем полсекунды для применения конфигурации
            time.sleep(0.5) 
            
        print(f"Конфигурация применена на {self.host}. Настройки сохранены в NVRAM.")
        self.tn.close()

def main():
    if not all([ADDR, USER, PASS]):
        print("!!! Ошибка: Проверь переменные окружения ES_ADDR, ES_USER, ES_PASS")
        sys.exit(1)

    manager = ZelaxSwitch(ADDR, USER, PASS)
    parser = argparse.ArgumentParser(description="Zabbix cli-утилита для управления Zelax портами и вланами")
    subparsers = parser.add_subparsers(dest="command")

    # Секция для портов (синонимы interface/port)
    for alias in ["interface", "port"]:
        p = subparsers.add_parser(alias)
        p.add_argument("iface", help="Имя порта, типа fe/0/1")
        p.add_argument("action", choices=["enable", "disable", "tags", "access"])
        p.add_argument("val", nargs="?", help="VLAN id или список через запятую")

    # Секция для вланов
    v = subparsers.add_parser("vlan")
    v.add_argument("action", choices=["add", "del"])
    v.add_argument("id", help="Номер VLAN")

    args = parser.parse_args()
    commands = []

    # Логика команд
    if args.command in ["interface", "port"]:
        commands.append(f"interface {args.iface}")
        if args.action == "disable":
            commands.append("shutdown")
        elif args.action == "enable":
            commands.append("no shutdown")
        elif args.action == "access":
            # Чистый доступ в одном влане
            commands.append("switchport mode access")
            commands.append(f"switchport access vlan {args.val}")
        elif args.action == "tags":
            # Траниковый порт с тэгами
            commands.append("switchport mode trunk")
            commands.append(f"switchport trunk allowed vlan {args.val}")

    elif args.command == "vlan":
        if args.action == "add":
            commands.append(f"vlan {args.id}")
        elif args.action == "del":
            commands.append(f"no vlan {args.id}")

    if commands:
        manager.push_config(commands)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()