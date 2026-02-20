# escli
Zabbix Custom-Script: escli. Скрипт для быстрого управления портами и вланами для коммутаторов Zelax (ZES) из Web интерфейса Zabbix.

**ENV переменные:**
- `ES_ADDR`: IP адрес нашего свича
- `ES_USER`: Логин (обычно admin)
- `ES_PASS`: Пароль

**Сборка:**
docker build -t escli .

**Запуск (Примеры):**
- docker run --env-file .env escli port fe/0/1 enable
- docker run --env-file .env escli port fe/0/1 tags 10,20,30
- docker run --env-file .env escli port fe/0/2 access 10