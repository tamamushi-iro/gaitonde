# Gaitonde

A Discord Bot

Systemd service file examples:

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

Note:
- a huge initial chunck of the code was written on putty-nano editor, where default indentaion was 8-spaced Tabs, still left in files.

A few common commands:
```
BDayWisher:
  addBoii      Add BDay and Boii. Usage: <command> @<bdboi-mention> "<name>"...
  age          Show Boii's age
  listBoiis    Show DB Entries
  nextBday     Show the upcoming birthdays in the Guild for the next 3 months.
  removeBoii   Remove a mentioned Boii
  showBoii     Show Boii Info
General:
  avatar       
  kanye        
  nft          
  osle         
  ping         
  rage         
  rgb          
  tava         
  thecoolernft 
  upparsegaya  
  why          
Radio:
  doumo        Join user's VC.
  jp           Now playing on the LISTEN.moe J-Pop stream.
  kaero        Leave the VC.
  moe          Play LISTEN.moe's J-Pop Stream.
YTStream:
  join         Join a user's VC.
  leave        Leave the VC.
  np           Now playing track
  pause        Toggles Pause/Play
  play         Plays the requested song.
  queue        
  remove       
  search       Queries the YouTube API and returns five results to select from.
  skip         Skips current track
  soundboard   Options: sw, ss, yay, ting, weebAsylum, rage
  stop         Stops playing Moozic
  url          Plays the media in the url.
​No Category:
  help         Shows this message
```