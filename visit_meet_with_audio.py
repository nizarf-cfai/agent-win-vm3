#!/usr/bin/env python3
"""
Google Meet Visitor with Audio Bridge
Joins Google Meet and works with the audio bridge for Gemini AI integration

This script:
1. Joins Google Meet using saved Chrome profile
2. Configures audio to work with the audio bridge
3. Allows Gemini AI to participate in the meeting

Usage:
1. First run: python audio_bridge.py
2. Then run: python visit_meet_with_audio.py
"""

import time
from pathlib import Path
from DrissionPage import ChromiumPage, ChromiumOptions
import pyautogui
from PIL import Image, ImageDraw

# MEET_LINK = "https://meet.google.com/xdt-graq-fcm"
MEET_LINK = "https://meet.google.com/vqh-jfsc-vid"
 
# Use the same profile directory as the profile manager
PROFILE_DIR = Path(__file__).parent / "chrome_profile"

def create_chrome_options():
    """Create Chrome options using the saved profile - EXACT copy from chrome_profile_manager.py"""
    co = ChromiumOptions()
    
    # Set the profile directory
    co.set_user_data_path(str(PROFILE_DIR))
    co.set_argument('--profile-directory=Default')
    

    
    return co



def main(MEET_LINK):
    """Visit Google Meet with audio bridge integration"""
    print("=" * 60)
    print("Google Meet Visitor with Audio Bridge")
    print("=" * 60)
    print(f"Meet Link: {MEET_LINK}")
    print(f"Using profile: {PROFILE_DIR}")
    
    # Check if profile exists
    default_profile = PROFILE_DIR / "Default"
    if not default_profile.exists():
        print("❌ No saved profile found!")
        print("Please run 'python chrome_profile_manager.py' first to set up your profile.")
        return False
    
    # Show profile status
    profile_files = list(default_profile.iterdir())
    print(f"✓ Found saved profile with {len(profile_files)} files")
    print("You should be automatically logged in!")
    
    # Check for key login files
    login_files = ["Login Data", "Preferences"]
    for file_name in login_files:
        file_path = default_profile / file_name
        if file_path.exists():
            print(f"✓ {file_name} found")
        else:
            print(f"○ {file_name} missing")
    

    try:
        # Create Chrome options
        options = create_chrome_options()
        
        # Launch Chrome
        print("\nLaunching Chrome...")
        page = ChromiumPage(options)
        
        print("✓ Chrome launched successfully!")
        print(f"Navigating to: {MEET_LINK}")
        
        # Visit the Google Meet link
        page.get(MEET_LINK)
        
        print("✓ Navigated to Google Meet")
        print("You should now be logged in automatically!")
        
        # Wait 2 seconds after page load
        print("Waiting 2 seconds after page load...")
        time.sleep(2)
        
        # Click on permission tag
        print("Looking for permission tag...")
        try:
            # Try to find and click the permission element
            permission_element = page.ele('tag:permission', timeout=5)
            if permission_element:
                print("✓ Found permission tag, clicking...")
                permission_element.click()
                print("✓ Clicked permission tag")
                
                # Wait 2 seconds after clicking
                print("Waiting 2 seconds after clicking permission...")
                time.sleep(2)
            else:
                print("○ Permission tag not found")
        except Exception as e:
            print(f"○ Could not find or click permission tag: {e}")
        
        # Click on button with specific attribute
        print("Looking for button with data-promo-anchor-id='w5gBed'...")
        try:
            # Try to find and click the button with the specific attribute
            button_element = page.ele('@data-promo-anchor-id=w5gBed', timeout=5)
            if button_element:
                print("✓ Found button with data-promo-anchor-id='w5gBed', clicking...")
                button_element.click()
                print("✓ Clicked button")
                
                # Wait 2 seconds after clicking
                print("Waiting 2 seconds after clicking button...")
                time.sleep(2)
            else:
                print("○ Button with data-promo-anchor-id='w5gBed' not found")
        except Exception as e:
            print(f"○ Could not find or click button: {e}")

        time.sleep(1)
        
        # Test coordinate checking function
        print("\n🎯 Testing coordinate checking...")
        print("You can now test coordinates by calling: check_coordinate(x, y)")
        print("Example: check_coordinate(400, 300)")
        # meet_ops(page)

        # Keep the browser open
        print("\n🔄 Meeting is now active with audio bridge integration!")
        print("Press Ctrl+C to close the meeting and stop the audio bridge...")
        
        try:
            # Keep running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Closing meeting...")
        
        print("✓ Actions completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Chrome is installed and accessible.")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Google Meet Visitor with Audio Bridge")
    parser.add_argument("--link", type=str, required=True, help="Google Meet link to join")
    args = parser.parse_args()

    main(args.link)