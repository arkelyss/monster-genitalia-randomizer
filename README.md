# Monster Genitalia Randomizer (Alpha Phase)

This project is currently in early alpha. Designs, features, and functionality may break or change at any time. If you would like to help shape its development, you can participate in the following ways:

- Alpha testing by cloning the 'develop' branch and using the program.
- Reporting bugs or submitting PRs.
- Requesting features, offering suggestions, and sharing feedback.
- Creating UI assets such as icons, art, and screenshots.
- Donations of any amount so that I can stay caffeinated.


# Introduction
Monster Genitalia Randomizer is the official successor to an old cli app created for Monster Hunter World, published directly to NexusMods (https://www.nexusmods.com/monsterhunterworld/mods/7102). At its core, the original app was a randomizer for Monster Hunter World genitalia mods. It provided features like randomized mod deployment, synchronized results via seed sharing, and the ability to customize preferences with keyword filters.

The original app was limited in scope, buggy, and not user-friendly.  This project aims to provide more features and quality of life additions, such as:

- A simple GUI
- Automatic mod installation (drag and drop supported)
- Timer-based randomized while client is running
- Shared coop settings for total synchronization
- Community participation and collaboration
- Expanded filters for in-depth customization
- Lightweight symlink deployment system


# Alpha Testing Guidance
As an alpha tester, you will be exploring uncharted territory. Some days the everything might run perfectly, and other times nothing will function at all. You may encounter features and designs you love, only to have them snatched away during a future update.

Don't let this scare you; use it to your advantage! Instead of trying to make things work, see if you can find ways to break them. If you discover something you love and it gets removed, start a discussion to bring it back. Alpha testing is for thinking outside the box; we can get more organized when Beta rolls around.

**When in doubt, follow these suggestions:**
1. Update frequently. Changes are constantly happening, so check back daily!
2. Try to break things instead of trying to make them work.
3. Look beyond bugs and code, sometimes it's about what you want.
4. Use GitHub to make your voice heard:
    - Report bugs here: https://github.com/arkelyss/monster-genitalia-randomizer/issues
    - Discuss here: https://github.com/arkelyss/monster-genitalia-randomizer/discussions
    - Submit your own code here: https://github.com/arkelyss/monster-genitalia-randomizer/pulls
    - Contact the dev here: arkelysstm@gmail.com


# Requirements

- Linux/Windows OS
- Python 3.14 (https://www.python.org/downloads/)
- Git (https://git-scm.com/)


# Installation
There are two ways to install MGR: CMD/Terminal or the ZIP File. I highly recommend using CMD/Terminal, you will have a much easier time later.

## Windows CMD
1. Open Command Prompt as Administrator.
2. Change the directory to wherever you want MGR installed: 'cd <directory-path>'.
3. Run the following commands:
    ```console
    # Clone MGR
    git clone -b develop https://github.com/arkelyss/monster_genitalia_randomizer.git

    # Enter the project directory
    cd monster-genitalia-randomizer
    ```
4. Open File Explorer and run 'start_mgr.bat' directly, or do it from the Command Prompt:
    ```console
    # Start MGR
    start_mgr.bat
    ```
5. The script will run and check for updates (say yes to any updates). Afterwards, a menu will appear.
6. Select `1. Set up virtual environment`.
7. Select `3. Start MGR` to start the program.


## Linux Terminal
1. Open a new terminal.
2. Change the directory to wherever you want the project installed: 'cd <directory-path>'.
3. Run the following commands:
    ```console
    # Clone MGR
    git clone -b develop https://github.com/arkelyss/monster_genitalia_randomizer.git

    # Enter the directory
    cd monster-genitalia-randomizer

    # Make all scripts executable
    sudo chmod +x *

    # Run MGR
    ./start_mgr.sh
    ```
4. The script will run and check for updates (say yes to any updates). Afterwards, a menu will appear.
5. Select `1. Set up virtual environment`.
6. Select `3. Start MGR` to start the program.


## ZIP File
1. Navigate to MGR's GitHub page and change the branch from `main` to `develop` (or use this link: https://github.com/arkelyss/monster-genitalia-randomizer/tree/develop).
2. Look for the green **<> Code** button and click it.
3. Select *Download ZIP* from the dropdown.
4. Unpack the ZIP file anywhere.
5. Navigate into the *monster-genitalia-randomizer* directory.
6. Run *start_mgr.bat* (*start_mgr.sh* on Linux).
7. A menu will appear in your CMD/Terminal window.
6. Select `1. Set up virtual environment`.
7. Select `3. Start MGR` to start the program.


# Updating
The way you will update MGR changes depending on how you installed it. CMD/Terminal users will have a much easier time keeping their installation updated.

## CMD/Terminal
1. Run the `start_mgr` script.
2. It will check for updates. When prompted, input 'y' to accept and download.
3. Alternatively, select `2. Check for updates` from the script menu, then use 'y' to accept and download.

## ZIP File
1. Delete your old *monster-genitalia-randomizer* directory (don't worry, your configurations and settings are safe).
2. Follow the original installation instructions for ZIP Files (see the Installation chapter above).