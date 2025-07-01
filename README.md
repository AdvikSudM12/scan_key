# Enhanced Multi-Provider GitHub Scanner v3.0

**Автор:** PRIZRAKJJ  
**Telegram:** [t.me/SafeVibeCode](https://t.me/SafeVibeCode)

🤖 **Мульти-провайдерный сканер API-ключей для поиска и валидации ключей OpenAI, Anthropic (Claude) и Google Gemini в GitHub репозиториях.**

## 🚀 Новые возможности v3.0

- ✅ **Мульти-провайдерная поддержка**: OpenAI, Anthropic (Claude), Google Gemini
- ✅ **Интеллектуальная идентификация** провайдера по формату ключа
- ✅ **Раздельное хранение** валидных ключей по провайдерам
- ✅ **Расширенные поисковые запросы** для каждого провайдера
- ✅ **Накопительный режим** - ключи сохраняются, не перезаписываются
- ✅ **Умное управление лимитами** GitHub API
- ✅ **Кэширование результатов** для избежания повторной обработки


**Быстрый старт**

**Windows (Рекомендуется)**

**Запустите quick_start.bat**

**Выберите пункт меню для установки и настройки**

**Следуйте интерактивным инструкциям**



## 📋 Структура проекта

```
📁 Проект/
├── 📄 enhanced_scanner.py           # Основной мульти-провайдерный сканер
├── 📄 ai_providers_key_patterns.py  # Паттерны и валидаторы для провайдеров
├── 📄 test_multi_provider_scanner.py # Тесты функциональности
├── 📄 .env                          # Переменные окружения
├── 📄 requirements.txt              # Python зависимости
│
├── 📄 valid_openai_keys.json        # Валидные ключи OpenAI
├── 📄 valid_anthropic_keys.json     # Валидные ключи Anthropic
├── 📄 valid_google_gemini_keys.json # Валидные ключи Google Gemini
└── 📄 scanner_cache.json            # Кэш обработанных файлов
```

## 🔧 Настройка и установка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env`:

```env
# GitHub API токен (обязательно для избежания лимитов)
GITHUB_TOKEN=your_github_token_here

# Тестовые ключи для валидации (опционально)
OPENAI_API_KEY=sk-your-test-openai-key
ANTHROPIC_API_KEY=sk-ant-your-test-anthropic-key
GOOGLE_API_KEY=AIza-your-test-google-key
```

### 3. Запуск сканера

```bash
# Основное сканирование
python enhanced_scanner.py

# Очистка кэша
python enhanced_scanner.py --clear-cache

# Тестирование функциональности
python test_multi_provider_scanner.py
```

## 🤖 Поддерживаемые провайдеры

### OpenAI
- **Форматы ключей**: `sk-*`, `sk-proj-*`
- **Переменные**: `OPENAI_API_KEY`, `OPENAI_KEY`
- **Валидация**: OpenAI API `/v1/models`

### Anthropic (Claude)
- **Форматы ключей**: `sk-ant-*`
- **Переменные**: `ANTHROPIC_API_KEY`, `CLAUDE_API_KEY`
- **Валидация**: Anthropic API `/v1/messages`

### Google Gemini
- **Форматы ключей**: `AIza*`
- **Переменные**: `GOOGLE_API_KEY`, `GEMINI_API_KEY`
- **Валидация**: Google AI API `/v1/models`

## 📊 Файлы результатов

Каждый провайдер имеет свой файл для накопления валидных ключей:

### valid_openai_keys.json
```json
{
  "scan_info": {
    "timestamp": "2025-01-01T12:00:00",
    "provider": "openai",
    "valid_keys_found": 5,
    "total_keys_tested": 150
  },
  "valid_keys": [
    {
      "api_key": "sk-...",
      "provider": "openai",
      "repository": "owner/repo",
      "file_path": ".env",
      "found_at": "2025-01-01T12:00:00",
      "validation_status": "valid"
    }
  ]
}
```

## 🎯 Особенности извлечения ключей

Сканер умеет находить ключи в различных контекстах:

```python
# Переменные окружения
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY="sk-ant-..."
GOOGLE_API_KEY=AIza...

# В коде Python
openai.api_key = "sk-..."
client = Anthropic(api_key="sk-ant-...")

# В JSON/YAML
{
  "openai_key": "sk-...",
  "anthropic_key": "sk-ant-...",
  "google_key": "AIza..."
}

# HTTP заголовки
Authorization: Bearer sk-...
x-api-key: sk-ant-...
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
python test_multi_provider_scanner.py

# Результат:
# ✅ ПРОШЕЛ - Идентификация провайдеров
# ✅ ПРОШЕЛ - Извлечение ключей
# ✅ ПРОШЕЛ - Файловая структура
# ✅ ПРОШЕЛ - Поисковые запросы
# 📈 Результат: 4/4 тестов прошли
# 🎉 Все тесты успешно пройдены! Сканер готов к работе.
```

## 📈 Статистика использования

После сканирования вы увидите подробную статистику:

```
🎉 НАЙДЕННЫЕ ВАЛИДНЫЕ КЛЮЧИ ПО ПРОВАЙДЕРАМ:
============================================================

🤖 OPENAI:
   1. 🔑 sk-proj-abc...xyz
      📦 Репозиторий: user/openai-project
      📄 Файл: .env
      🕒 Обновлен: 2024-12-30

🤖 ANTHROPIC:
   1. 🔑 sk-ant-api03-def...uvw
      📦 Репозиторий: user/claude-bot
      📄 Файл: config.py
      🕒 Обновлен: 2024-12-29

🤖 GOOGLE GEMINI:
   1. 🔑 AIzaSy123...ABC
      📦 Репозиторий: user/gemini-app
      📄 Файл: credentials.json
      🕒 Обновлен: 2024-12-28

📊 ИТОГО: 3 валидных ключей найдено
```

---

**Enhanced Multi-Provider GitHub Scanner v3.0** - мощный инструмент для поиска и валидации API-ключей различных AI-провайдеров в открытых GitHub репозиториях. Используйте ответственно и в соответствии с условиями использования GitHub API.

## Возможности

- 🔍 Поиск упоминаний `OPENAI_API_KEY` в коде GitHub репозиториев
- 🔑 Извлечение API ключей в различных форматах (старые `sk-...` и новые `sk-proj-...`)
- ✅ Валидация найденных ключей через OpenAI API
- � **Система кэширования**: автоматическое сохранение прогресса и избежание повторной обработки
- �📊 Сортировка результатов по свежести (самые новые файлы первыми)
- 🔄 **Промежуточное сохранение**: автоматическое сохранение каждые 10 файлов
- 💾 Сохранение результатов с подробной статистикой
- 🎯 Расширенные паттерны поиска для различных контекстов
- 🖥️ Интерактивное меню установки и запуска (Windows)
- 🧪 Автоматическое тестирование функции валидации
- ⚡ **Быстрый перезапуск**: продолжение с места остановки при прерывании

## Быстрый старт

### Windows (Рекомендуется)
1. Запустите `quick_start.bat`
2. Выберите пункт меню для установки и настройки
3. Следуйте интерактивным инструкциям

### Ручная установка

#### 1. Проверка Python
```bash
# Проверьте версию Python (требуется 3.7+):
python --version      # Windows/Linux (стандартная установка)
py --version          # Windows (Python Launcher)
python3 --version     # Linux/macOS (если есть Python 2 и 3)
```

#### 2. Установка зависимостей
Выберите подходящую команду для вашей системы:

**Windows:**
```batch
# Стандартная установка Python:
pip install -r requirements.txt

# Python Launcher (рекомендуется):
py -m pip install -r requirements.txt

# Если установлено несколько версий Python:
py -3 -m pip install -r requirements.txt
py -3.9 -m pip install -r requirements.txt

# Альтернативный способ:
python -m pip install -r requirements.txt
```

**Linux/Ubuntu/Debian:**
```bash
# Стандартная команда:
pip3 install -r requirements.txt

# Если pip3 не найден:
python3 -m pip install -r requirements.txt

# Для виртуального окружения:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Установка через apt (если нужен pip):
sudo apt update
sudo apt install python3-pip
```

**macOS:**
```bash
# Homebrew Python:
pip3 install -r requirements.txt

# Системный Python:
python3 -m pip install -r requirements.txt

# Если Python установлен через pyenv:
pyenv exec pip install -r requirements.txt
```

**Универсальные команды:**
```bash
# Работает на всех системах:
python -m pip install -r requirements.txt

# Обновление pip перед установкой:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Установка в пользовательскую директорию:
python -m pip install --user -r requirements.txt
```

#### 3. Создание конфигурации
1. Скопируйте `.env.example` в `.env`:
```bash
# Windows:
copy .env.example .env

# Linux/macOS:
cp .env.example .env
```

2. Настройте токены в `.env` файле (откройте в текстовом редакторе)

## Использование

### С интерактивным меню (Windows)
```batch
quick_start.bat
```

### Прямой запуск скрипта

**Windows:**
```batch
# Python Launcher (рекомендуется):
py enhanced_scanner.py

# Стандартная команда:
python enhanced_scanner.py

# Если установлено несколько версий:
py -3 enhanced_scanner.py
py -3.9 enhanced_scanner.py

# Через модуль:
py -m enhanced_scanner
python -m enhanced_scanner
```

**Linux/Ubuntu/Debian:**
```bash
# Основные команды:
python3 enhanced_scanner.py
python enhanced_scanner.py

# Если файл имеет права на выполнение:
./enhanced_scanner.py

# Через модуль:
python3 -m enhanced_scanner

# В виртуальном окружении:
source venv/bin/activate
python enhanced_scanner.py
```

**macOS:**
```bash
# Homebrew Python:
python3 enhanced_scanner.py

# Системный Python:
/usr/bin/python3 enhanced_scanner.py

# Если установлен через pyenv:
pyenv exec python enhanced_scanner.py

# Исполняемый файл:
./enhanced_scanner.py
```

**Универсальные команды (работают везде):**
```bash
# Через интерпретатор Python:
python enhanced_scanner.py

# Через модуль (если настроена поддержка):
python -m enhanced_scanner

# С явным указанием пути:
python ./enhanced_scanner.py
python "enhanced_scanner.py"
```

**Запуск с параметрами:**
```bash
# Очистка кэша:
python enhanced_scanner.py --clear-cache
python enhanced_scanner.py --reset
python enhanced_scanner.py -r

# С отладкой:
python enhanced_scanner.py --debug

# В тихом режиме:
python enhanced_scanner.py --quiet
```

## Файлы проекта

- `enhanced_scanner.py` - Основной улучшенный скрипт сканирования
- `quick_start.bat` - Интерактивное меню установки и запуска (Windows)
- `requirements.txt` - Зависимости Python
- `.env` - Файл конфигурации (создается автоматически)
- `scanner_cache.json` - Кэш обработанных файлов (создается автоматически)
- `README.md` - Документация

## Интерактивное меню (quick_start.bat)

### Возможности меню:
1. **Установить зависимости и запустить** - полная автоматическая установка
2. **Только установить зависимости** - установка без запуска
3. **Только запустить сканер** - запуск с проверкой зависимостей
4. **Очистить кэш и запустить** - сброс кэша для полного пересканирования
5. **Выход** - корректное завершение

### Автоматические проверки:
- ✅ Проверка наличия и версии Python
- ✅ Проверка установленных зависимостей  
- ✅ Создание и настройка файла `.env`
- ✅ Загрузка кэша обработанных файлов
- ✅ Предварительное тестирование функции валидации
- ✅ Автоматическое сохранение прогресса

## Настройка токенов

### GitHub Personal Access Token
1. Перейдите на https://github.com/settings/tokens
2. Создайте новый токен (classic)
3. Выберите права: `public_repo`
4. Скопируйте токен и добавьте в `.env`

### OpenAI API Key
1. Перейдите на https://platform.openai.com/account/api-keys
2. Создайте новый API ключ
3. Скопируйте ключ и добавьте в `.env`

## Новые возможности v2.1

### 💾 Система кэширования
- **Автоматическое сохранение прогресса**: кэш обновляется каждые 10 обработанных файлов
- **Быстрый перезапуск**: при повторном запуске пропускаются уже обработанные файлы
- **Сохранение при прерывании**: при Ctrl+C кэш автоматически сохраняется
- **Управление кэшем**: возможность очистки через меню или параметр `--clear-cache`
- **Статистика кэша**: отображение количества обработанных файлов и размера кэша

### 🔧 Улучшенное меню
- **Обновленный интерфейс**: более интуитивное управление
- **Очистка кэша**: отдельный пункт меню для сброса прогресса
- **Возврат в меню**: автоматический возврат после завершения операций
- **Обработка ошибок**: корректная обработка прерываний и ошибок

### Расширенные паттерны поиска
- Поиск старых ключей: `sk-[A-Za-z0-9]{48}`
- Поиск новых project ключей: `sk-proj-...`
- Поиск в различных контекстах (JSON, YAML, переменные окружения, код)

### Улучшенная сортировка
- Сортировка по дате обновления (`updated`)
- Сортировка по релевантности (`indexed`)
- Фильтрация по датам создания файлов

### Расширенные поисковые запросы
1. `OPENAI_API_KEY`
2. `sk- AND openai`
3. `sk-proj AND openai` (новые ключи)
4. `OPENAI_API_KEY AND .env`
5. `openai.api_key AND python`
6. `sk- pushed:>2024-01-01` (свежие файлы)
7. И многие другие...

## Конфигурация (.env файл)

Основные параметры:
```properties
# GitHub Personal Access Token (увеличивает лимиты API)
GITHUB_TOKEN=your_github_token_here

# OpenAI API Key (для тестирования функции валидации)
OPENAI_API_KEY=your_openai_api_key_here

# Настройки сканирования
MAX_PAGES_PER_QUERY=3         # Максимальное количество страниц для обработки на запрос
DELAY_BETWEEN_REQUESTS=1      # Пауза между запросами к GitHub API (в секундах)
DELAY_BETWEEN_KEY_TESTS=2     # Пауза между проверками ключей через OpenAI API (в секундах)

# Файлы для сохранения
OUTPUT_FILE=enhanced_valid_openai_keys.json  # Результаты сканирования
CACHE_FILE=scanner_cache.json                # Кэш обработанных файлов
```

## Управление кэшем

### Что кэшируется:
- 📁 **Обработанные файлы**: URL-ы уже просканированных файлов
- 🔑 **Протестированные ключи**: хэши уже проверенных API ключей
- 📊 **Статистика**: количество обработанных файлов и найденных ключей

### Команды управления кэшем:
```bash
# Просмотр статистики кэша (при запуске):
python enhanced_scanner.py

# Очистка кэша:
python enhanced_scanner.py --clear-cache
python enhanced_scanner.py --reset
python enhanced_scanner.py -r

# Очистка через меню:
quick_start.bat -> пункт 4
```

### Автоматическое сохранение:
- ⚡ Каждые 10 обработанных файлов
- 🛑 При прерывании сканирования (Ctrl+C)
- ✅ При нормальном завершении работы
- ❌ При критических ошибках

## Тестирование функции валидации

Если в `.env` файле указан `OPENAI_API_KEY`, скрипт автоматически:
1. 🧪 Тестирует функцию валидации с вашим ключом
2. ✅ Подтверждает корректность работы валидации
3. ⚠️ Предупреждает о проблемах и предлагает решения
4. 🔍 Переходит к основному сканированию

## Результаты сканирования

### Основной файл результатов
Результаты сохраняются в JSON файл `enhanced_valid_openai_keys.json` с подробной информацией:

```json
{
  "scan_info": {
    "timestamp": "2025-07-01T12:00:00",
    "total_keys_tested": 45,
    "valid_keys_found": 3,
    "files_processed": 1250,
    "success_rate": "6.67%",
    "cache_used": true,
    "cached_files_skipped": 850
  },
  "valid_keys": [
    {
      "key": "sk-proj-...",
      "repository": "username/repo",
      "file_path": "config/.env",
      "file_url": "https://github.com/username/repo/blob/main/config/.env",
      "updated_at": "2025-06-15",
      "size": 1024,
      "found_at": "2025-07-01T12:30:00"
    }
  ]
}
```

### Кэш файл
Кэш сохраняется в `scanner_cache.json`:
```json
{
  "processed_files": [
    "https://github.com/user/repo/blob/main/file1.py",
    "https://github.com/user/repo/blob/main/file2.js"
  ],
  "tested_keys": [
    "abc123...hash",
    "def456...hash"
  ],
  "last_updated": "2025-07-01T12:00:00",
  "files_count": 1250,
  "keys_count": 45
}
```

## Системные требования

- **OS:** Windows 10+ (для интерактивного меню), Linux, macOS
- **Python:** 3.7 или выше
- **RAM:** Минимум 512 MB
- **Интернет:** Стабильное подключение для работы с API
- **Дисковое пространство:** 50 MB для установки

## Устранение неполадок

### Проблемы с Python
```bash
# Проверка версии Python
python --version

# Если Python не найден, установите с официального сайта
# https://www.python.org/downloads/
```

### Проблемы с зависимостями
```bash
# Переустановка зависимостей
pip install --upgrade -r requirements.txt

# Очистка кеша pip
pip cache purge
```

### Проблемы с кэшем
```bash
# Очистка кэша сканера:
python enhanced_scanner.py --clear-cache

# Или через меню:
quick_start.bat -> пункт 4

# Ручное удаление файла кэша:
del scanner_cache.json  # Windows
rm scanner_cache.json   # Linux/macOS
```

### Проблемы с токенами
- Проверьте правильность токенов в `.env` файле
- Убедитесь в наличии прав `public_repo` для GitHub токена
- Проверьте квоты и лимиты для OpenAI API

## Changelog v2.1

### 🆕 Новые функции:
- 💾 **Система кэширования**: автоматическое сохранение и загрузка прогресса
- ⚡ **Быстрый перезапуск**: продолжение с места остановки
- 🔄 **Промежуточное сохранение**: автоматическое сохранение каждые 10 файлов
- 🧹 **Управление кэшем**: очистка через меню или параметры командной строки
- 📊 **Расширенная статистика**: отображение информации о кэше

### 🔧 Улучшения интерфейса:
- 🖥️ Обновленное интерактивное меню `quick_start.bat`
- 🔄 Автоматический возврат в главное меню после операций
- 🛑 Корректная обработка прерываний (Ctrl+C)
- 📋 Улучшенные сообщения о статусе и прогрессе

### 🚀 Оптимизация производительности:
- ⚡ Избежание повторной обработки файлов
- 💾 Экономия API запросов через кэширование
- 🔄 Интеллектуальное восстановление после прерывания
- 📈 Ускорение повторных запусков в 3-5 раз

---

## Changelog v2.0

### Новые функции:
- ✨ Интерактивное меню установки и запуска
- 🧪 Автоматическое тестирование функции валидации
- 🎯 Расширенные паттерны поиска для новых форматов ключей
- 📊 Улучшенная статистика и отчетность
- 🔧 Автоматическая настройка конфигурации

### Улучшения:
- 🚀 Повышенная производительность сканирования
- 🛡️ Улучшенная обработка ошибок и исключений
- 💫 Более дружелюбный пользовательский интерфейс
- 📝 Расширенная документация и справка

## Этические соображения

⚠️ **ВАЖНО**: Этот инструмент предназначен только для образовательных целей и тестирования безопасности.

### Правила использования:
- ✅ Используйте только для изучения и понимания проблем безопасности
- ✅ Сообщайте о найденных уязвимостях владельцам репозиториев
- ✅ Соблюдайте условия использования GitHub и OpenAI
- ❌ Не используйте найденные ключи для несанкционированного доступа
- ❌ Не нарушайте законодательство вашей страны

### Ответственность:
Автор не несет ответственности за неправомерное использование инструмента. Используйте только в законных целях.

## Поддержка

- 💬 **Telegram канал:** [t.me/SafeVibeCode](https://t.me/SafeVibeCode)
- 📧 **Вопросы и предложения:** пишите в Telegram
- 🐛 **Баги и улучшения:** создавайте Issues в репозитории

## Благодарности

Спасибо всем, кто тестировал и помогал улучшать этот инструмент! 🙏

## Лицензия

Этот проект предназначен только для образовательных целей и исследований в области безопасности. Используйте ответственно и в соответствии с законодательством.

---

**© 2025 PRIZRAKJJ | [Telegram: t.me/SafeVibeCode](https://t.me/SafeVibeCode)**
