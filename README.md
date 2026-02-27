# macOS VNC Remote Monitor

A simple Python script to set up VNC (Screen Sharing) on macOS for remote monitoring. Perfect for monitoring your Mac while traveling.

## What It Does

Automatically configures your Mac for remote VNC access:

- ✅ Enables macOS Screen Sharing service
- ✅ Sets up password authentication
- ✅ Configures firewall exceptions
- ✅ Creates background monitoring service
- ✅ Provides connection information

## Requirements

- macOS 10.14+
- Python 3 (pre-installed)
- sudo privileges

## Usage

```bash
sudo python3 mac_vnc_monitor.py
```

The script will prompt you for:
1. **VNC Password** (min 8 characters)
2. **Port Number** (default: 5900)
3. **Confirmation** to proceed

## How It Works

### 1. Enables Screen Sharing
Uses macOS's Remote Management tools:
```bash
launchctl load -w /System/Library/LaunchDaemons/com.apple.screensharing.plist
```

### 2. Sets VNC Password
Configures authentication via Apple Remote Desktop:
```bash
/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart \
  -configure -clientopts -setvnclegacy -vnclegacy yes -setvncpw -vncpw "PASSWORD"
```

### 3. Configures Firewall
Adds Screen Sharing to allowed services if firewall is enabled:
```bash
/usr/libexec/ApplicationFirewall/socketfilterfw --add AppleVNCServer
```

### 4. Creates Background Monitor
Generates a LaunchAgent that checks VNC status every 60 seconds and restarts if needed. Ensures VNC stays active after reboots.

### 5. Verifies Setup
- Checks Screen Sharing service is running
- Verifies VNC port is listening
- Displays connection information

## Connecting

**From Mac:**
- Finder → `⌘K` → `vnc://YOUR_IP_ADDRESS`

**From other devices:**
- Use any VNC client (RealVNC, TightVNC, etc.)
- Connect to `YOUR_IP_ADDRESS:5900`

## Remote Access

**Local network:** Use the local IP shown by the script

**Outside your network:**
1. Forward port 5900 on your router to your Mac's local IP
2. Use your public IP to connect

**Better option:** Use a VPN (Tailscale, WireGuard, etc.) for secure access

## Security Notes

⚠️ **Important:**
- Use a strong password
- VNC is not encrypted by default - use VPN or SSH tunnel for sensitive work
- Only expose ports when needed

## Troubleshooting

**Check if VNC is running:**
```bash
sudo launchctl list | grep screensharing
```

**Check background service:**
```bash
launchctl list | grep vnc
```

**View logs:**
```bash
tail -f /tmp/vnc_keepalive.log
```

**Manually start/stop:**
```bash
# Start VNC
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.screensharing.plist

# Stop VNC
sudo launchctl unload /System/Library/LaunchDaemons/com.apple.screensharing.plist
```

## Uninstall

```bash
# Stop VNC
sudo launchctl unload /System/Library/LaunchDaemons/com.apple.screensharing.plist

# Remove background service
rm ~/Library/LaunchAgents/com.user.vnc.keepalive.plist
killall Python
rm /tmp/vnc_keepalive.py
```

## License

MIT License

---

**⭐ Star this repo if you find it useful!**
