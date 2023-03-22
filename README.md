# Gaitonde

A Discord Bot

To run as a systemd service, Systemd service file examples:

```desktop
$ cat /etc/systemd/system/gaitonde-bot.service 
[Unit]
Description=Gandtode Discord Bot
After=wss-listen-moe.service

[Service]
Type=simple
User=not_root
Group=not_root
WorkingDirectory=/path/to/gaitonde
ExecStart=/usr/bin/python3 /path/to/gaitonde/gaitonde.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

```desktop
$ cat /etc/systemd/system/wss-listen-moe.service 
[Unit]
Description=WSS LISTEN.moe Bash Script

[Service]
Type=simple
User=not_root
Group=not_root
WorkingDirectory=/path/to/gaitonde
ExecStart=/usr/bin/python3 /path/to/gaitonde/wss_listen_moe.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

Expected Directory Structure:
```X Font Directory Index
gaitonde/
├── .backups/
│   └── ...
├── .errors/
│   ├── archive/
│   │   └── ...
│   ├── gaitonde_error.log
│   └── wss_error.log
├── sounds/
│   ├── sound_file.mp3
│   └── ...
├── .env
├── .gitignore
├── bDayBoiis.db
├── gaitonde_bDayWisher.py
├── gaitonde_general.py
├── gaitonde_radio.py
├── gaitonde_ytstream.py
├── gaitonde.py
├── LICENSE
├── nowPlaying.json
├── README.md
├── requirements.txt
└── wss_listen_moe.py
```
