@echo off

REM Переходим в папку проекта
cd /d "%~dp0"

REM Активируем виртуальное окружение
call venv\Scripts\activate

REM Запуск
python etl.py history
python etl.py daily