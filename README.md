# Monster Genitalia Randomizer

This project is currently in early alpha. Designs, features, and functionality may break or change at any time. If you would like to help shape this project's development, you can participate in the following ways:

- Alpha testing by cloning the 'develop' branch and using the program.
- Reporting bugs and submitting PRs.
- Requesting features, offering suggestions, and sharing feedback.
- Creating UI assets such as icons, art, and screenshots.
- Donations of any amount so that I can stay caffeinated.


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
