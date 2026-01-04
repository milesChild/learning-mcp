#!/bin/bash
trap "kill 0" EXIT

source ./venv/bin/activate
python server.py &
sleep 1
ngrok http 8000 > /dev/null 2>&1 &

echo "Running MCP server and ngrok. Logs:"
wait
