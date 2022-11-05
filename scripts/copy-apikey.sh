#!/bin/bash
echo "Copying IBM Cloud apikey into development environment..."
docker cp ~/.bluemix/apikey.json nyu:/home/vscode 
docker exec nyu sudo chown vscode:vscode /home/vscode/apikey.json
echo "Complete"
