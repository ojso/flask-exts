#!/bin/sh
sh babel.sh
curl -F "files[/messages.pot]=@messages.pot" http://api.crowdin.net/api/project/flask-exts/update-file?key=`cat ~/.crowdin.flaskexts.key`
