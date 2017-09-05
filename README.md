# fall-2017-website

## Server
To run, do `./runserver.sh`
In order to have the server listen on port 80, must be run as sudo
Student roster must be loaded into `backup.csv` to whitelist users
 - see sample `backup.csv` to see example
 - backups made using lecturer commands are stored in backup.csv

## Lecturer Commands
Lecturer commands are in `lecture.sh`
 - Open a new lecture session with `./lecture.sh open-session`
 - Close an open lecture session with `./lecture.sh close-session`
 - Make server backup with `./lecture.sh backup`


