# Dynv6 DDNS Update Tool for Windows

## Introduction

This software is a Dynv6 DDNS update tool specifically designed for the Windows system. It runs in the form of a system tray icon, offering convenient operation and rich features. Through a simple right - click menu, users can easily view the status, modify settings, restart the program, etc.

## Software Technologies

This software is mainly developed based on the following technologies:

- **Python**: As the primary programming language, Python provides a strong foundation for software development with its concise and readable syntax and rich library support.
- **Requests**: Used for HTTP communication with the Dynv6 server to implement the update operation of dynamic domain name resolution.
- **PyQt5**: Used to create the graphical user interface (GUI) of the software, including the system tray icon and the configuration editing window, providing users with an intuitive operating interface.

## Open-Source License

This project adopts the MIT open-source license.

## Features

1. **System Tray Icon**: The software resides in the system as a tray icon, not taking up much desktop space and facilitating easy operation at any time.

2. **Rich Right - Click Menu Functions**:

   - **View Status**: Click this option to open the log file, allowing users to easily understand the software's running status and historical records at any time.
   - **Settings**: Open the configuration editing window, where users can modify and adjust the relevant parameters of Dynv6 DDNS.
   - **Restart**: One - click to restart the software to ensure that the latest configuration of the software takes effect.
   - **Start on Boot**: Support setting the software to start automatically when the system boots, enabling the software to run automatically without manual intervention.
   - **Pause**: Temporarily stop the DDNS update operation, facilitating users to perform temporary control when needed.
   - **Restore Configuration**: Restore the software's configuration to the previously saved state, avoiding configuration loss due to accidental operations.
   - **Exit**: Safely close the software and release system resources.

## Software Interface Display
![tray_menu.png](resources%2Ftray_menu.png)![config_editor.png](resources%2Fconfig_editor.png)


## Usage Instructions

1. **Installation**: Download the software to the software installation directory. After decompressing it, double-click the executable file to run it.
2. **Initial Configuration**: When running the software for the first time, the configuration editing window will automatically pop up (if not, right - click on the software system tray icon and select "Settings"). Fill in the relevant Dynv6 information, such as Domain, Token, etc.
3. **Save the Configuration File**: After correctly filling in the relevant configuration, click the "Save" button. The software will restart and start updating the DDNS.
4. **View Status**: If you need to view the running status, right - click on the software system icon and select the "View Status" option to open the log file.
5. **Auto - Start**: If you need to set the software to start automatically when the system boots, right - click on the software system icon and select the "Start on Boot" option.

## Notes

- Please ensure that the entered Dynv6 information is accurate; otherwise, the DDNS update may fail.
- If the software encounters abnormal situations, you can try "Reset Configuration" or "Restart" the software.

## Feedback and Suggestions

If you encounter any problems or have any suggestions during use, welcome to submit an Issue in the GitHub repository. I will handle and reply to it in a timely manner.

## Thanks for Your Support

Thank you for using this software! If you find this software helpful to you, welcome to give a Star★ to our GitHub repository. Your support is our driving force for continuous progress!