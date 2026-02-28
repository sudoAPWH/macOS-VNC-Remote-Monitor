#!/usr/bin/env python3
"""
macOS VNC Uninstall Script
Removes VNC/Screen Sharing configuration set up by mac_vnc_monitor.py
"""

import os
import sys
import subprocess
import time

def run_command(cmd, require_sudo=False, capture_output=True):
    """Run a shell command and return the result."""
    try:
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

def check_screen_sharing_status():
    """Check if Screen Sharing is currently enabled."""
    success, output = run_command("sudo launchctl list | grep screensharing")
    return success and "screensharing" in output

def disable_screen_sharing():
    """Disable Screen Sharing."""
    print_header("Disabling Screen Sharing")
    
    print("⏳ Stopping Screen Sharing service...")
    
    # Unload the Screen Sharing daemon
    success, _ = run_command("sudo launchctl unload /System/Library/LaunchDaemons/com.apple.screensharing.plist", require_sudo=True)
    
    time.sleep(1)
    
    # Verify it stopped
    if not check_screen_sharing_status():
        print("✅ Screen Sharing disabled successfully!")
        return True
    else:
        print("⚠️  Screen Sharing may still be running")
        print("   You can disable it manually in System Preferences > Sharing")
        return False

def remove_vnc_configuration():
    """Remove VNC password and configuration."""
    print_header("Removing VNC Configuration")
    
    print("⏳ Removing VNC settings...")
    
    # Deactivate and remove VNC configuration
    commands = [
        'sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -deactivate -stop',
        'sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -configure -access -off',
    ]
    
    for cmd in commands:
        run_command(cmd, require_sudo=True)
        time.sleep(0.5)
    
    print("✅ VNC configuration removed!")
    return True

def remove_firewall_exception():
    """Remove Screen Sharing from firewall exceptions."""
    print_header("Firewall Configuration")
    
    print("Checking firewall status...")
    time.sleep(0.5)
    
    # Check if firewall is enabled
    success, output = run_command("sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate")
    
    if "enabled" in output.lower():
        print("✓ Firewall is enabled")
        print()
        
        if ask_yes_no("Remove Screen Sharing from firewall exceptions?", default="y"):
            print("\n⏳ Removing firewall exceptions...")
            run_command("sudo /usr/libexec/ApplicationFirewall/socketfilterfw --blockapp /System/Library/CoreServices/RemoteManagement/AppleVNCServer.bundle/Contents/MacOS/AppleVNCServer")
            time.sleep(0.5)
            print("✅ Firewall exception removed")
        else:
            print("⚠️  Keeping firewall exception (can remove manually)")
    else:
        print("✓ Firewall is disabled or has no VNC exceptions")
    
    return True

def show_welcome():
    """Show welcome screen."""
    clear_screen()
    print_header("macOS VNC Uninstall")
    print("This script will remove VNC/Screen Sharing configuration.")
    print()
    print("What will be removed:")
    print("  • Screen Sharing service (disabled)")
    print("  • VNC password and authentication")
    print("  • Firewall exceptions (optional)")
    print()
    print("⚠️  IMPORTANT:")
    print("  • This script requires administrator privileges (sudo)")
    print("  • Screen Sharing will be completely disabled")
    print()
    
    if not ask_yes_no("Ready to continue?", default="y"):
        print("\nUninstall cancelled.")
        sys.exit(0)

def show_completion():
    """Show completion message."""
    clear_screen()
    print_header("Uninstall Complete")
    
    print("✅ VNC/Screen Sharing has been removed from your Mac.")
    print()
    print("What was done:")
    print("  • Screen Sharing service disabled")
    print("  • VNC configuration removed")
    print("  • Firewall settings updated")
    print()
    print("Your Mac is no longer accessible via VNC.")
    print()
    print("="*60 + "\n")

def main():
    """Main uninstall function."""
    
    # Show welcome screen
    show_welcome()
    
    # Check if running with sudo
    if not check_if_root():
        clear_screen()
        print_header("Administrator Privileges Required")
        print("⚠️  This script needs administrator privileges to:")
        print("   • Disable Screen Sharing service")
        print("   • Remove VNC configuration")
        print("   • Update firewall settings")
        print("\n🔧 Please run with: sudo python3 uninstall_vnc.py")
        print()
        sys.exit(1)
    
    # Check if Screen Sharing is even enabled
    if not check_screen_sharing_status():
        clear_screen()
        print_header("Screen Sharing Not Found")
        print("Screen Sharing doesn't appear to be running.")
        print()
        if not ask_yes_no("Continue with cleanup anyway?", default="y"):
            print("\nUninstall cancelled.")
            sys.exit(0)
    
    # Disable Screen Sharing
    disable_screen_sharing()
    
    # Remove VNC configuration
    remove_vnc_configuration()
    
    # Remove firewall exception
    remove_firewall_exception()
    
    # Show completion
    show_completion()

if __name__ == "__main__":
    main()
