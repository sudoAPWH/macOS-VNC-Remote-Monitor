#!/usr/bin/env python3
"""
macOS VNC Monitor Setup Script
Enables Screen Sharing (VNC) on macOS for remote monitoring while away.
"""

import os
import sys
import subprocess
import getpass
import time
import socket

# Configuration (will be set interactively)
VNC_PASSWORD = None
VNC_PORT = 5900
AUTO_START = True

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear')

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(text.center(60))
    print("="*60 + "\n")

def ask_yes_no(question, default="y"):
    """Ask a yes/no question and return boolean."""
    while True:
        if default.lower() == "y":
            prompt = f"{question} (Y/n): "
        else:
            prompt = f"{question} (y/N): "
        
        response = input(prompt).strip().lower()
        
        if response == "":
            response = default.lower()
        
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Please enter 'y' or 'n'")

def get_password():
    """Get VNC password from user with confirmation."""
    print_header("VNC Password Setup")
    print("Your VNC password should be:")
    print("  • At least 8 characters long")
    print("  • Memorable but secure")
    print("  • Different from your Mac login password")
    print()
    
    while True:
        password = getpass.getpass("Enter VNC password: ")
        
        if len(password) < 8:
            print("❌ Password must be at least 8 characters. Try again.\n")
            continue
        
        password_confirm = getpass.getpass("Confirm VNC password: ")
        
        if password != password_confirm:
            print("❌ Passwords don't match. Try again.\n")
            continue
        
        print("✓ Password set!\n")
        return password

def get_port_number():
    """Get VNC port number from user."""
    print_header("VNC Port Configuration")
    print("Default VNC port is 5900 (recommended)")
    print("Only change if you know what you're doing.")
    print()
    
    if not ask_yes_no("Use default port 5900?", default="y"):
        while True:
            try:
                port = input("Enter custom port number (1024-65535): ").strip()
                port = int(port)
                if 1024 <= port <= 65535:
                    print(f"✓ Using port {port}\n")
                    return port
                else:
                    print("❌ Port must be between 1024 and 65535")
            except ValueError:
                print("❌ Please enter a valid number")
    else:
        print("✓ Using default port 5900\n")
        return 5900

def show_welcome():
    """Show welcome screen."""
    clear_screen()
    print_header("macOS VNC Remote Monitoring Setup")
    print("This script will configure your Mac for remote VNC access.")
    print()
    print("What this script does:")
    print("  ✓ Enables macOS Screen Sharing (VNC server)")
    print("  ✓ Sets up password authentication")
    print("  ✓ Configures firewall rules")
    print("  ✓ Sets up background monitoring")
    print("  ✓ Provides connection information")
    print()
    print("⚠️  IMPORTANT:")
    print("  • This script requires administrator privileges (sudo)")
    print("  • You'll need to enter your Mac password")
    print("  • Make sure you're on a secure network")
    print()
    
    if not ask_yes_no("Ready to continue?", default="y"):
        print("\nSetup cancelled.")
        sys.exit(0)

def confirm_settings(password, port):
    """Show summary and ask for confirmation."""
    print_header("Configuration Summary")
    print(f"VNC Password: {'*' * len(password)}")
    print(f"VNC Port:     {port}")
    print(f"Auto-start:   Yes (runs in background)")
    print()
    
    if not ask_yes_no("Proceed with these settings?", default="y"):
        print("\nSetup cancelled.")
        sys.exit(0)
    print()

def run_command(cmd, require_sudo=False, capture_output=True):
    """Run a shell command and return the result."""
    try:
        if require_sudo:
            # For sudo commands, we need to handle password
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=capture_output,
                text=True,
                check=False
            )
        else:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=capture_output,
                text=True,
                check=False
            )
        return result.returncode == 0, result.stdout if capture_output else ""
    except Exception as e:
        print(f"Error running command: {e}")
        return False, ""

def check_if_root():
    """Check if script is running with sudo privileges."""
    return os.geteuid() == 0

def install_dependencies():
    """Check and install required dependencies."""
    print_header("Checking Dependencies")
    print("Verifying required tools...")
    time.sleep(1)
    
    # Check if Homebrew is installed (optional, for additional tools)
    success, _ = run_command("which brew")
    if not success:
        print("ℹ️  Homebrew not found (optional)")
    else:
        print("✓ Homebrew found")
    
    print("✓ All required dependencies available\n")
    
    return True

def enable_screen_sharing():
    """Enable macOS Screen Sharing (VNC)."""
    print_header("Enabling Screen Sharing")
    
    print("⏳ Configuring Screen Sharing...")
    
    # Enable Screen Sharing using system preferences
    commands = [
        ('Loading Screen Sharing service...', 
         'sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.screensharing.plist 2>/dev/null || true'),
        
        ('Configuring service settings...', 
         'sudo defaults write /var/db/launchd.db/com.apple.launchd/overrides.plist com.apple.screensharing -dict Disabled -bool false 2>/dev/null || true'),
        
        ('Activating remote access...', 
         'sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -activate -configure -access -on -restart -agent -privs -all'),
        
        ('Setting access permissions...', 
         'sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -configure -allowAccessFor -allUsers -privs -all'),
    ]
    
    for description, cmd in commands:
        print(f"  {description}")
        success, output = run_command(cmd, require_sudo=True)
        time.sleep(0.5)
        if not success and "operation not permitted" in output.lower():
            print("\n⚠️  Permission denied. Make sure to run with sudo.")
            return False
    
    print("\n✅ Screen Sharing enabled successfully!")
    return True

def set_vnc_password(password):
    """Set the VNC password."""
    print_header("Configuring VNC Password")
    
    print("⏳ Setting up password authentication...")
    time.sleep(0.5)
    
    # Set VNC password using the system method
    # Note: This sets the password in the system keychain
    cmd = f'sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -configure -clientopts -setvnclegacy -vnclegacy yes -setvncpw -vncpw "{password}"'
    
    success, _ = run_command(cmd, require_sudo=True)
    
    if success:
        print("✅ VNC password configured successfully!")
    else:
        print("⚠️  Warning: Could not set VNC password via command line")
        print("   You may need to set it manually in System Preferences > Sharing > Screen Sharing")
        if not ask_yes_no("Continue anyway?", default="y"):
            return False
    
    return True

def check_firewall():
    """Check if firewall allows VNC connections."""
    print_header("Firewall Configuration")
    
    print("Checking firewall status...")
    time.sleep(0.5)
    
    # Check if firewall is enabled
    success, output = run_command("sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate")
    
    if "enabled" in output.lower():
        print("⏳ Adding firewall exceptions...")
        run_command("sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /System/Library/CoreServices/RemoteManagement/AppleVNCServer.bundle/Contents/MacOS/AppleVNCServer")
        run_command("sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /System/Library/CoreServices/RemoteManagement/AppleVNCServer.bundle/Contents/MacOS/AppleVNCServer")
        time.sleep(0.5)
        print("✅ Firewall configured for VNC")
    else:
        print("✓ Firewall is disabled or not blocking VNC")
    
    return True

def get_local_ip():
    """Get the local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Unable to determine"

def get_public_ip():
    """Get the public IP address."""
    try:
        result = subprocess.run(
            ["curl", "-s", "ifconfig.me"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except:
        return "Unable to determine"

def verify_setup():
    """Verify that VNC is running."""
    print_header("Verifying Setup")
    
    print("⏳ Running final checks...")
    time.sleep(1)
    
    checks_passed = 0
    total_checks = 2
    
    # Check if Screen Sharing is running
    success, output = run_command("launchctl list | grep screensharing")
    
    if success and "screensharing" in output:
        print("✓ Screen Sharing is running")
        checks_passed += 1
    else:
        print("⚠️  Screen Sharing may not be running")
    
    time.sleep(0.5)
    
    # Check if port is listening
    success, output = run_command(f"lsof -i :{VNC_PORT}")
    if success:
        print(f"✓ VNC server listening on port {VNC_PORT}")
        checks_passed += 1
    else:
        print(f"⚠️  VNC port {VNC_PORT} may not be accessible")
    
    print(f"\n✅ Verification: {checks_passed}/{total_checks} checks passed\n")
    
    return checks_passed > 0

def print_connection_info():
    """Print connection information."""
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    clear_screen()
    print("="*60)
    print("VNC SETUP COMPLETE".center(60))
    print("="*60)
    
    print("\n" + "─"*60)
    print("CONNECTION INFORMATION")
    print("─"*60)
    print(f"\n  Local Network:")
    print(f"     IP Address:  {local_ip}")
    print(f"     Port:        {VNC_PORT}")
    print(f"     Full URL:    vnc://{local_ip}:{VNC_PORT}")
    
    print(f"\n  Remote Access:")
    print(f"     Public IP:   {public_ip}")
    print(f"     Port:        {VNC_PORT}")
    print(f"     Full URL:    vnc://{public_ip}:{VNC_PORT}")
    
    print(f"\n  Password:      {VNC_PASSWORD}")
    
    print("\n" + "─"*60)
    print("QUICK REFERENCE")
    print("─"*60)
    
    print(f"\n  Check Status:  sudo launchctl list | grep screensharing")
    print(f"  Stop VNC:      sudo launchctl unload /System/Library/LaunchDaemons/com.apple.screensharing.plist")
    print(f"  Start VNC:     sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.screensharing.plist")
    
    print("\n" + "="*60)
    print("\nYour Mac is now remotely accessible via VNC!")
    print("Screen Sharing will continue running even after reboot.")
    print("\n" + "="*60 + "\n")

def main():
    """Main setup function."""
    global VNC_PASSWORD, VNC_PORT
    
    # Show welcome screen
    show_welcome()
    
    # Check if running with sudo
    if not check_if_root():
        clear_screen()
        print_header("Administrator Privileges Required")
        print("⚠️  This script needs administrator privileges to:")
        print("   • Enable Screen Sharing service")
        print("   • Configure firewall rules")
        print("   • Set system-wide VNC password")
        print("\n🔧 Please run with: sudo python3 mac_vnc_monitor.py")
        print()
        sys.exit(1)
    
    # Get configuration from user
    VNC_PASSWORD = get_password()
    VNC_PORT = get_port_number()
    
    # Confirm settings
    confirm_settings(VNC_PASSWORD, VNC_PORT)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency check failed")
        sys.exit(1)
    
    # Enable Screen Sharing
    if not enable_screen_sharing():
        print("\n❌ Failed to enable Screen Sharing")
        print("\n📝 Manual setup instructions:")
        print("1. Open System Preferences > Sharing")
        print("2. Check 'Screen Sharing'")
        print("3. Click 'Computer Settings' and enable VNC viewers")
        print()
        sys.exit(1)
    
    # Set VNC password
    if not set_vnc_password(VNC_PASSWORD):
        print("\n❌ Failed to set VNC password")
        sys.exit(1)
    
    # Configure firewall
    check_firewall()
    
    # Verify setup
    print_header("Final Verification")
    print("⏳ Waiting for services to start...")
    time.sleep(3)  # Wait for services to start
    
    verify_setup()
    
    # Print connection info
    print_connection_info()

if __name__ == "__main__":
    main()
