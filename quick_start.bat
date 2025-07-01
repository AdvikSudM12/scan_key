@echo off
chcp 65001 >nul
title Enhanced Multi-Provider GitHub Scanner v3.0
color 0A

:menu
cls
echo ================================================================================
echo                Enhanced Multi-Provider GitHub Scanner v3.0
echo                Поддержка: OpenAI, Anthropic (Claude), Google Gemini
echo                            by PRIZRAKJJ
echo                     Telegram: https://t.me/SafeVibeCode
echo ================================================================================
echo.
echo 🚀 ГЛАВНОЕ МЕНЮ
echo ────────────────────────────────────────────────────────────────────────────────
echo.
echo 1. 🔍 Запустить мульти-провайдерный сканер
echo 2. 🧪 Запустить тесты функциональности  
echo 3. 📦 Установить зависимости
echo 4. ⚙️  Настроить переменные окружения
echo 5. 🗑️  Очистить кэш
echo 6. 📊 Показать статистику файлов
echo 7. ❓ Помощь
echo 8. 🚪 Выход
echo.
echo ────────────────────────────────────────────────────────────────────────────────
set /p choice="Выберите опцию (1-8): "

if "%choice%"=="1" goto run_scanner
if "%choice%"=="2" goto run_tests
if "%choice%"=="3" goto install_deps
if "%choice%"=="4" goto setup_env
if "%choice%"=="5" goto clear_cache
if "%choice%"=="6" goto show_stats
if "%choice%"=="7" goto help
if "%choice%"=="8" goto exit

echo ❌ Неверный выбор. Нажмите любую клавишу...
pause >nul
goto menu

:run_scanner
cls
echo 🔍 ЗАПУСК МУЛЬТИ-ПРОВАЙДЕРНОГО СКАНЕРА
echo ────────────────────────────────────────────────────────────────────────────────
echo.
py enhanced_scanner.py
echo.
echo ────────────────────────────────────────────────────────────────────────────────
echo Сканирование завершено. Нажмите любую клавишу для возврата в меню...
pause >nul
goto menu

:run_tests
cls
echo 🧪 ЗАПУСК ТЕСТОВ ФУНКЦИОНАЛЬНОСТИ
echo ────────────────────────────────────────────────────────────────────────────────
echo.
py test_multi_provider_scanner.py
echo.
echo ────────────────────────────────────────────────────────────────────────────────
echo Тестирование завершено. Нажмите любую клавишу для возврата в меню...
pause >nul
goto menu

:install_deps
cls
echo 📦 УСТАНОВКА ЗАВИСИМОСТЕЙ
echo ────────────────────────────────────────────────────────────────────────────────
echo.
echo Проверка наличия Python...
py --version 2>nul
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python с python.org
    echo.
    pause
    goto menu
)

echo ✅ Python найден
echo.
echo Установка зависимостей из requirements.txt...
py -m pip install -r requirements.txt
echo.
echo ────────────────────────────────────────────────────────────────────────────────
echo Установка завершена. Нажмите любую клавишу для возврата в меню...
pause >nul
goto menu

:setup_env
cls
echo ⚙️ НАСТРОЙКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
echo ────────────────────────────────────────────────────────────────────────────────
echo.
if exist .env (
    echo 📄 Найден существующий .env файл:
    echo.
    type .env
    echo.
    echo ────────────────────────────────────────────────────────────────────────────────
    set /p recreate="Пересоздать файл? (y/N): "
    if /i not "%recreate%"=="y" goto menu
)

echo.
echo Создание .env файла...
echo.

set /p github_token="🔑 Введите GitHub токен (для избежания лимитов API): "
set /p openai_key="🤖 Введите OpenAI API ключ (опционально, для тестов): "
set /p anthropic_key="🤖 Введите Anthropic API ключ (опционально): "
set /p google_key="🤖 Введите Google API ключ (опционально): "

echo # Enhanced Multi-Provider GitHub Scanner v3.0 Config > .env
echo # by PRIZRAKJJ - https://t.me/SafeVibeCode >> .env
echo # Токены API для доступа к различным сервисам >> .env
echo. >> .env
echo # GitHub API токен (обязательно для избежания лимитов) >> .env
echo GITHUB_TOKEN=%github_token% >> .env
echo. >> .env
echo # Тестовые ключи для валидации (опционально) >> .env
if not "%openai_key%"=="" echo OPENAI_API_KEY=%openai_key% >> .env
if not "%anthropic_key%"=="" echo ANTHROPIC_API_KEY=%anthropic_key% >> .env
if not "%google_key%"=="" echo GOOGLE_API_KEY=%google_key% >> .env

echo.
echo ✅ Файл .env создан успешно!
echo.
echo ────────────────────────────────────────────────────────────────────────────────
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto menu

:clear_cache
cls
echo 🗑️ ОЧИСТКА КЭША
echo ────────────────────────────────────────────────────────────────────────────────
echo.
py enhanced_scanner.py --clear-cache
echo.
echo ────────────────────────────────────────────────────────────────────────────────
echo Очистка завершена. Нажмите любую клавишу для возврата в меню...
pause >nul
goto menu

:show_stats
cls
echo 📊 СТАТИСТИКА ФАЙЛОВ
echo ────────────────────────────────────────────────────────────────────────────────
echo.
echo 📄 Файлы результатов по провайдерам:
echo.
if exist valid_openai_keys.json (
    for /f %%i in ('py -c "import json; print(len(json.load(open('valid_openai_keys.json'))['valid_keys']))"') do (
        echo 🤖 OpenAI: %%i валидных ключей
    )
) else (
    echo 🤖 OpenAI: файл не найден
)

if exist valid_anthropic_keys.json (
    for /f %%i in ('py -c "import json; print(len(json.load(open('valid_anthropic_keys.json'))['valid_keys']))"') do (
        echo 🤖 Anthropic: %%i валидных ключей
    )
) else (
    echo 🤖 Anthropic: файл не найден
)

if exist valid_google_gemini_keys.json (
    for /f %%i in ('py -c "import json; print(len(json.load(open('valid_google_gemini_keys.json'))['valid_keys']))"') do (
        echo 🤖 Google Gemini: %%i валидных ключей
    )
) else (
    echo 🤖 Google Gemini: файл не найден
)

echo.
echo 💾 Кэш:
if exist scanner_cache.json (
    for /f %%i in ('py -c "import json; print(len(json.load(open('scanner_cache.json'))['processed_files']))"') do (
        echo 📂 Обработано файлов: %%i
    )
    for /f %%i in ('py -c "import json; print(len(json.load(open('scanner_cache.json'))['tested_keys']))"') do (
        echo 🔑 Протестировано ключей: %%i
    )
) else (
    echo 📂 Кэш не найден
)

echo.
echo ────────────────────────────────────────────────────────────────────────────────
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto menu

:help
cls
echo ❓ ПОМОЩЬ
echo ────────────────────────────────────────────────────────────────────────────────
echo.
echo 🤖 Enhanced Multi-Provider GitHub Scanner v3.0
echo    by PRIZRAKJJ - Telegram: https://t.me/SafeVibeCode
echo.
echo Этот инструмент предназначен для поиска и валидации API-ключей различных
echo AI-провайдеров в открытых GitHub репозиториях.
echo.
echo 📋 Поддерживаемые провайдеры:
echo   • OpenAI (GPT) - ключи вида sk-... и sk-proj-...
echo   • Anthropic (Claude) - ключи вида sk-ant-...
echo   • Google Gemini - ключи вида AIza...
echo.
echo 🔧 Быстрый старт:
echo   1. Запустите "Установить зависимости"
echo   2. Настройте переменные окружения (обязательно GitHub токен)
echo   3. Запустите сканер
echo.
echo 🚨 Важные замечания:
echo   • Используйте GitHub токен для избежания лимитов API
echo   • Сканер создает отдельные файлы для каждого провайдера
echo   • Кэш сохраняет прогресс между запусками
echo   • Используйте инструмент ответственно
echo.
echo 📞 Поддержка:
echo   • Запустите тесты для проверки работоспособности
echo   • Проверьте .env файл при ошибках
echo   • Убедитесь в подключении к интернету
echo   • Telegram: https://t.me/SafeVibeCode
echo.
echo ────────────────────────────────────────────────────────────────────────────────
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto menu

:exit
cls
echo 👋 Спасибо за использование Enhanced Multi-Provider GitHub Scanner v3.0!
echo    by PRIZRAKJJ - Telegram: https://t.me/SafeVibeCode
echo.
timeout /t 2 >nul
exit

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
