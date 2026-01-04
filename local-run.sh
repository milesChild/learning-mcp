#!/bin/bash
trap "kill 0" EXIT

source ./.venv/bin/activate
python server.py &
sleep 1

# Start ngrok in the background and capture output
ngrok http 8000 > ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok's API to be ready
for i in {1..10}; do
    if curl --silent --max-time 1 http://localhost:4040/api/tunnels > /dev/null; then
        break
    else
        sleep 1
    fi
done

NGROK_URL=$(curl --silent http://localhost:4040/api/tunnels | grep -o '"public_url":"https:[^"]*' | sed 's/"public_url":"//')
echo "Running MCP server and ngrok."
echo "ngrok public URL: $NGROK_URL"
echo "Logs:"
wait
