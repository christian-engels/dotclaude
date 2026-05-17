Start a Claude Code Remote Control server so you can connect from claude.ai/code or the Claude iOS app. Runs as a background process — no new terminal window needed, works whether you're at your desk or remote.

**Before starting the server, use the AskUserQuestion tool to ask:** "What should this session be named? (This label appears in claude.ai/code and the iOS app.)"

Then use the Bash tool to run, substituting the user's answer for `SESSION_NAME`:

```bash
# Kill any existing remote-control server
pkill -f "claude remote-control" 2>/dev/null || true
sleep 0.5

# Start in background, log output so we can read the connection link
printf 'y\n' | CLAUDECODE="" claude remote-control --name "SESSION_NAME" --permission-mode bypassPermissions > /tmp/claude-rc.log 2>&1 &
RC_PID=$!
echo "Remote Control starting (PID: $RC_PID)..."

# Wait for the connection link to appear in the log
for i in $(seq 1 10); do
    sleep 1
    if grep -q "https://" /tmp/claude-rc.log 2>/dev/null; then
        break
    fi
done

cat /tmp/claude-rc.log
```

Then display the connection URL to the user so they can open it on their iOS device. The server keeps running in the background after this session ends.

**Key details:**
- `CLAUDECODE=""` clears the parent session's `CLAUDECODE=1` flag, which would otherwise block initialisation
- `--permission-mode bypassPermissions` auto-approves all tool calls
- The log file is at `/tmp/claude-rc.log` if you need to check it later
- To stop the server: `pkill -f "claude remote-control"`
