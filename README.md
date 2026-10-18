# YouTube Channel Backup

Скрипт для бэкапа YouTube канала/плейлиста через [yt-dlp](https://github.com/yt-dlp/yt-dlp) + ffmpeg.

- Инкрементальные повторные запуски: уже скачанное не качается заново (`--download-archive`)
- В комплекте: видео, описание, обложка и info-json с метаданными
- Настраиваемое качество, ретраи, паузы против троттлинга
- ffmpeg встроен в пакет `imageio-ffmpeg` — ничего доустанавливать не нужно

## Требования

1. **Python 3.10+** — [скачать](https://www.python.org/downloads/)
2. **Node.js** — нужен yt-dlp как JS-рантайм для работы с защитой YouTube. Скачайте LTS-версию с [nodejs.org](https://nodejs.org) (либо установите deno)
3. **yt-dlp** — устанавливается через pip

## Порядок действий

### 1. Установка зависимостей Python

```bash
pip install -r requirements.txt
```

`yt-dlp`, `imageio-ffmpeg` (со встроенным ffmpeg) — этого достаточно.

### 2. Установка Node.js (JS-рантайм для yt-dlp)

Без JS-рантайма yt-dlp не сможет получить все форматы видео. Установите Node.js LTS с [nodejs.org](https://nodejs.org). При первом запуске скрипт автоматически докачает вспомогательный компонент (`--remote-components ejs:github`).

### 3. Запуск

```bash
# Обязательный минимум — только URL
python backup.py "https://www.youtube.com/@channel/videos"

# Свои параметры
python backup.py "https://www.youtube.com/@channel/videos" -o my_backup --quality 720

# Без пауз между запросами (быстрее, но выше риск троттлинга)
python backup.py "https://www.youtube.com/@channel/videos" --no-sleep
```

Повторный запуск с теми же параметрами пропустит уже скачанные видео (файл `archive.txt` в папке вывода).

### Аргументы командной строки

| Аргумент | По умолчанию | Описание |
|---|---|---|
| `url` (позиционный) | — | URL канала, плейлиста или видео (обязателен) |
| `-o, --output` | `backup_channel` | папка для сохранения |
| `--quality` | `1080` | максимальная высота видео (720/1080/2160) |
| `--no-sleep` | выключено | не делать паузы между запросами |

## Структура проекта

```
YouTube_Downloader/
├── backup.py               # Основной скрипт
├── requirements.txt        # Зависимости Python
├── .gitignore              # Правила игнорирования Git
├── README.md               # Этот файл
└── backup_channel/         # Сюда сохраняются видео (создаётся при запуске, в .gitignore)
```

## Возможные проблемы

- **Предупреждение про JS-рантайм** — установите Node.js, либо обновите yt-dlp: `pip install -U yt-dlp`
- **"Some formats may be missing"** — yt-dlp устарел, обновите: `pip install -U yt-dlp`
- **Ошибка кодировки** — скрипт использует UTF-8, убедитесь, что терминал поддерживает UTF-8
- **"ffmpeg не найден"** — выполните `pip install imageio-ffmpeg`

## Примечание

Скачивание видео может нарушать условия использования YouTube. Используйте скрипт только для контента, на который у вас есть права (собственный канал, с разрешения автора, под свободной лицензией).
