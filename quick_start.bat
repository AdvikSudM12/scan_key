@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title GitHub OpenAI Scanner - Меню запуска

:main_menu
cls
echo.
echo ==========================================
echo  GitHub OpenAI Scanner - Меню запуска
echo  by PRIZRAKJJ
echo  Telegram: https://t.me/SafeVibeCode
echo ==========================================
echo.

REM Проверяем наличие основных файлов
if not exist "enhanced_scanner.py" (
    echo ОШИБКА: Файл enhanced_scanner.py не найден!
    echo Убедитесь, что вы запускаете этот файл из папки с проектом.
    echo.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ОШИБКА: Файл requirements.txt не найден!
    echo.
    pause
    exit /b 1
)

echo Выберите действие:
echo.
echo [1] Установить зависимости и запустить сканер
echo [2] Только установить зависимости
echo [3] Только запустить сканер
echo [4] Очистить кэш сканера
echo [0] Выход
echo.
set /p choice="Введите номер (0-4): "

if "%choice%"=="1" goto :full_install_and_run
if "%choice%"=="2" goto :install_only
if "%choice%"=="3" goto :run_only
if "%choice%"=="4" goto :clear_cache
if "%choice%"=="0" goto :exit_program
echo.
echo Неверный выбор! Введите число от 0 до 4.
timeout /t 2 >nul
goto :main_menu

:full_install_and_run

echo Проверка Python...

REM Проверяем доступность Python
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=py
    echo Python найден ^(команда: py^)
    goto :install_deps
)

python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
    echo Python найден ^(команда: python^)
    goto :install_deps
)

python3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python3
    echo Python найден ^(команда: python3^)
    goto :install_deps
)

echo.
echo ОШИБКА: Python не найден!
echo Пожалуйста, установите Python 3.7+ с официального сайта:
echo https://www.python.org/downloads/
echo.
echo Во время установки обязательно отметьте:
echo - "Add Python to PATH"
echo - "Install pip"
echo.
pause
exit /b 1

:install_deps
echo.
echo Установка зависимостей...
%PYTHON_CMD% -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo ОШИБКА: Не удалось установить зависимости!
    echo Проверьте подключение к интернету и права доступа.
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Зависимости успешно установлены!
echo.

:check_env
REM Проверяем наличие .env файла
if not exist ".env" (
    echo ⚠️  ВНИМАНИЕ: Файл .env не найден!
    echo.
    echo Для работы сканера необходимо создать файл .env с вашими API ключами.
    echo Пример содержимого:
    echo.
    echo OPENAI_API_KEY=your_openai_api_key_here
    echo ANTHROPIC_API_KEY=your_anthropic_api_key_here
    echo GOOGLE_API_KEY=your_google_api_key_here
    echo.
    echo Хотите создать пустой .env файл сейчас? ^(y/n^)
    set /p create_env="Введите y для создания: "
    
    if /i "!create_env!"=="y" (
        echo # Добавьте ваши API ключи здесь > .env
        echo # OPENAI_API_KEY=your_openai_api_key_here >> .env
        echo # ANTHROPIC_API_KEY=your_anthropic_api_key_here >> .env
        echo # GOOGLE_API_KEY=your_google_api_key_here >> .env
        echo ✅ Файл .env создан! Не забудьте добавить в него ваши API ключи.
        echo.
    )
)

:run_scanner
echo 🚀 Запуск сканера...
echo.
%PYTHON_CMD% enhanced_scanner.py

echo.
echo ==========================================
echo Сканирование завершено!
echo.
echo 📺 Больше инструментов: https://t.me/SafeVibeCode
echo 👨‍💻 Автор: PRIZRAKJJ
echo ==========================================
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto :main_menu

:install_only
cls
echo.
echo ==========================================
echo  Установка зависимостей
echo ==========================================
echo.

echo Проверка Python...

REM Проверяем доступность Python
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=py
    echo Python найден ^(команда: py^)
    goto :install_deps_only
)

python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
    echo Python найден ^(команда: python^)
    goto :install_deps_only
)

python3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python3
    echo Python найден ^(команда: python3^)
    goto :install_deps_only
)

echo.
echo ОШИБКА: Python не найден!
echo Пожалуйста, установите Python 3.7+ с официального сайта:
echo https://www.python.org/downloads/
echo.
echo Во время установки обязательно отметьте:
echo - "Add Python to PATH"
echo - "Install pip"
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto :main_menu

:install_deps_only
echo.
echo Установка зависимостей...
%PYTHON_CMD% -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo ОШИБКА: Не удалось установить зависимости!
    echo Проверьте подключение к интернету и права доступа.
    echo.
    echo Нажмите любую клавишу для возврата в меню...
    pause >nul
    goto :main_menu
)

echo.
echo ✅ Зависимости успешно установлены!
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto :main_menu

:run_only
cls
echo.
echo ==========================================
echo  Запуск сканера
echo ==========================================
echo.

echo Проверка Python...

REM Проверяем доступность Python
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=py
    echo Python найден ^(команда: py^)
    goto :check_env_only
)

python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
    echo Python найден ^(команда: python^)
    goto :check_env_only
)

python3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python3
    echo Python найден ^(команда: python3^)
    goto :check_env_only
)

echo.
echo ОШИБКА: Python не найден!
echo Пожалуйста, установите Python 3.7+ с официального сайта:
echo https://www.python.org/downloads/
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto :main_menu

:check_env_only
REM Проверяем наличие .env файла
if not exist ".env" (
    echo ⚠️  ВНИМАНИЕ: Файл .env не найден!
    echo.
    echo Для работы сканера необходимо создать файл .env с вашими API ключами.
    echo Пример содержимого:
    echo.
    echo OPENAI_API_KEY=your_openai_api_key_here
    echo ANTHROPIC_API_KEY=your_anthropic_api_key_here
    echo GOOGLE_API_KEY=your_google_api_key_here
    echo.
    echo Хотите создать пустой .env файл сейчас? ^(y/n^)
    set /p create_env="Введите y для создания: "
    
    if /i "!create_env!"=="y" (
        echo # Добавьте ваши API ключи здесь > .env
        echo # OPENAI_API_KEY=your_openai_api_key_here >> .env
        echo # ANTHROPIC_API_KEY=your_anthropic_api_key_here >> .env
        echo # GOOGLE_API_KEY=your_google_api_key_here >> .env
        echo ✅ Файл .env создан! Не забудьте добавить в него ваши API ключи.
        echo.
    )
)

:run_scanner_only
echo 🚀 Запуск сканера...
echo.
%PYTHON_CMD% enhanced_scanner.py

echo.
echo ==========================================
echo Сканирование завершено!
echo.
echo 📺 Больше инструментов: https://t.me/SafeVibeCode
echo 👨‍💻 Автор: PRIZRAKJJ
echo ==========================================
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto :main_menu

:clear_cache
cls
echo.
echo ==========================================
echo  Очистка кэша сканера
echo ==========================================
echo.

echo Проверка Python...

REM Проверяем доступность Python
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=py
    echo Python найден ^(команда: py^)
    goto :run_clear_cache
)

python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
    echo Python найден ^(команда: python^)
    goto :run_clear_cache
)

python3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python3
    echo Python найден ^(команда: python3^)
    goto :run_clear_cache
)

echo.
echo ОШИБКА: Python не найден!
echo Для очистки кэша требуется Python.
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto :main_menu

:run_clear_cache
echo.
echo 🗑️ Очистка кэша сканера...
%PYTHON_CMD% enhanced_scanner.py --clear-cache

echo.
echo ✅ Очистка кэша завершена!
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto :main_menu

:exit_program
cls
echo.
echo ==========================================
echo  Спасибо за использование!
echo.
echo 📺 Больше инструментов: https://t.me/SafeVibeCode
echo 👨‍💻 Автор: PRIZRAKJJ
echo ==========================================
echo.
timeout /t 2 >nul
exit /b 0
