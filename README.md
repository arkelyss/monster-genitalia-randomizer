# Monster Genitalia Randomizer

This project is currently in early alpha. Designs, features, and functionality may break or change at any time. If you would like to help shape this project's development, you can participate in the following ways:

- Alpha testing by cloning the 'develop' branch and using the program.
- Reporting bugs and submitting PRs.
- Requesting features, offering suggestions, and sharing feedback.
- Creating UI assets such as icons, art, and screenshots.
- Donations of any amount so that I can stay caffeinated.


# What is it?
Monster Genitalia Randomizer is the successor of MGR Cli (https://www.nexusmods.com/monsterhunterworld/mods/7102). At the core, it's a mod manager for Monster Hunter World genitalia mods, providing quality of life features like randomizated deployment for variety, seed sharing for coop, and the ability to filter for different monster sexes.

While the original cli version was limited and unwieldy, its this successor aims to provide more features and quality of life additions. These include (but aren't limited to):

- An easily-navigatable GUI
- Automatic mod installation via drag-and-drop
- Timer-based randomized (no two hunts are predictable)
- Shared coop settings for total synchronization
- Community participation via mod identification
- Expanded filters for in-depth customization
- Lightweight symlink deployment


# Requirements

- Linux/Windows OS
- Python 3.14 (https://www.python.org/downloads/)
- Git (https://git-scm.com/)


# Installation
There are several ways to install MGR, but all of them lead to the same place: Eventually, you will need to run 'setup_venv.bat' (or setup_venv.sh for Linux). This script only needs to be run once after downloading MGR, or once after updating to a new version. Afterwards, you can just use 'start_mgr.bat' (or start_mgr.sh on Linux) to open the program.


## Windows CMD
1. Open a new CMD window.
2. Change the directory (using 'cd <directory-path>') to wherever you want the project installed.
3. Run the following commands:
    ```console
    # Clone MGR
    git clone https://github.com/arkelyss/monster-genitalia-randomizer.git

    # Open the directory
    cd monster-genitalia-randomizer

    # Switch to the 'develop' branch
    git switch develop
    ```
4. At this point you have two options. You can open File Explorer and run setup_venv.bat directly, then start_mgr.bat, or you can do it from the CMD.
    ```console
    # Run the setup script
    setup_venv.bat

    # Start MGR
    start_mgr.bat
    ```


## Linux Terminal
1. Open a new terminal.
2. Change the directory (using 'cd <directory-path>') to wherever you want the project installed.
3. Run the following commands:
    ```console
    # Clone MGR
    git clone https://github.com/arkelyss/monster-genitalia-randomizer.git

    # Open the directory
    cd monster-genitalia-randomizer

    # Switch to the 'develop' branch
    git switch develop

    # Make the scripts executable and run the setup
    sudo chmod +x setup_venv.sh start_mgr.sh
    ./setup_venv.sh

    # Start MGR
    ./start_mgr.sh
    ```


## ZIP File
1. Navigate to MGR's main GitHub page and change the branch from 'main' to 'develop' (or use this link to get there: https://github.com/arkelyss/monster-genitalia-randomizer/tree/develop).
2. Look for the green '<> Code' button and click it.
3. Select 'Download ZIP' from the dropdown.
4. Unpack the ZIP file anywhere.
5. Navigate into the 'monster-genitalia-randomizer' directory.
6. Run setup_venv (.bat on Windows, .sh on Linux).
7. Run start_mgr (.bat on Windows, .sh on Linux).
