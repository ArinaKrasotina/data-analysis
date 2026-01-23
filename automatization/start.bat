@echo off

REM Переходим в папку проекта
cd /d "%~dp0"

REM Активируем виртуальное окружение
call venv\Scripts\activate

REM Генерация данных
python generate-data.py

REM Загрузка в БД
python load-to-db.py

