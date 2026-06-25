# CSS Launcher (لانچر کانتر سورس)

یک لانچر ساده و شیک با تم دارک برای اجرای بازی Counter-Strike: Source (نسخه v.34) که آیپی IPv4 سیستم شما را نیز نمایش می‌دهد.

## ویژگی‌ها

- رابط گرافیکی ساده با تم تیره (Dark Theme)
- نمایش IPv4 سیستم به صورت خودکار
- اجرای مستقیم بازی با یک کلیک
- نیاز به نصب پایتون (نسخه exe مستقل است)

## پیش‌نیازها

- ویندوز 10 یا بالاتر
- پوشه `Counter Strike Source v.34` کنار فایل اجرایی لانچر (در همان مسیر)

## ساختار پوشه‌ها

```
.
├── CSS_Launcher.exe
├── Counter Strike Source v.34/
│   └── hl2.exe
└── README.md
```

> لانچر فایل `hl2.exe` را از مسیر `Counter Strike Source v.34` که در کنار فایل exe قرار دارد پیدا و اجرا می‌کند.

## اجرا

### نسخه آماده (exe)

روی `CSS_Launcher.exe` دابل‌کلیک کنید.

### اجرا از سورس (Python)

```bash
pip install -r requirements.txt
python css_launcher.py
```

## ساخت فایل exe از سورس

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "CSS_Launcher" css_launcher.py
```

فایل خروجی در پوشه `dist` ساخته می‌شود.

## توسعه‌دهنده

ساخته شده با Python + Tkinter.
