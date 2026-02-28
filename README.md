# macOS VNC Remote Monitor

A simple Python script to set up VNC (Screen Sharing) on macOS for remote monitoring. Perfect for monitoring your Mac while traveling.

## What It Does

Automatically configures your Mac for remote VNC access:

- ✅ Enables macOS Screen Sharing service
- ✅ Sets up password authentication
- ✅ Configures firewall exceptions
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
Uses macOS's Remote Management tools to activate Screen Sharing as a system service:
```bash
launchctl load -w /System/Library/LaunchDaemons/com.apple.screensharing.plist
```

Screen Sharing runs as a system daemon and will automatically start after reboots.

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

### 4. Verifies Setup
- Checks Screen Sharing service is running
- Verifies VNC port is listening
- Displays connection information (local & public IP)

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

**Manually start/stop:**
```bash
# Start
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.screensharing.plist

# Stop
sudo launchctl unload /System/Library/LaunchDaemons/com.apple.screensharing.plist
```

**Check port:**
```bash
lsof -i :5900
```

## Uninstall

To completely remove VNC configuration, use the uninstall script:

```bash
sudo python3 uninstall_vnc.py
```

The uninstall script will:
- Disable Screen Sharing service
- Remove VNC password and configuration
- Remove firewall exceptions (optional)

### Manual Uninstall

If you prefer to uninstall manually:

```bash
# Stop Screen Sharing
sudo launchctl unload /System/Library/LaunchDaemons/com.apple.screensharing.plist

# Remove VNC configuration
sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -deactivate -stop

# Or disable in System Preferences > Sharing > uncheck "Screen Sharing"
```

## License

MIT License

---

**⭐ Star this repo if you find it useful!**
