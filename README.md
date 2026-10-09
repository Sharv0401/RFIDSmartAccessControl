# RFID Smart Access Control System

## Project Overview

The RFID Smart Access Control System is an IoT-based project developed using a Raspberry Pi. It uses RFID cards to control access, records access attempts in a database, and provides a web dashboard to manage cards and view access logs.

The system is designed to demonstrate how RFID technology, Python programming, database management, MQTT communication, and web development can be combined in an access control application.

## Features

- RFID card scanning and access verification
- Active and inactive card management
- SQLite database for storing card details and access logs
- MQTT communication for access control events
- Web dashboard built with Flask
- Access logs for monitoring granted and denied attempts
- LED indicators and buzzer for access feedback

## Technologies Used

- **Hardware:** Raspberry Pi and RFID reader
- **Programming Language:** Python
- **Database:** SQLite
- **Web Framework:** Flask
- **Messaging Protocol:** MQTT
- **Version Control:** Git and GitHub

## Main Project Files

| File | Description |
|---|---|
| `access_control.py` | Main RFID scanning and access control program |
| `database.py` | Database operations and data management |
| `add_cards.py` | Script for registering RFID cards |
| `app.py` | Flask web dashboard |
| `.gitignore` | Excludes local and temporary files from GitHub |

## How to Run

1. Set up the required hardware and Python environment on the Raspberry Pi.
2. Install the required Python packages and ensure the MQTT broker is available.
3. Run the RFID access control program:

   ```bash
   python3 access_control.py
   ```

4. In a separate terminal, start the web dashboard:

   ```bash
   python3 app.py
   ```

5. Open the dashboard in a browser using the Raspberry Pi's IP address and port `5000`:

   ```text
   http://<raspberry-pi-ip>:5000
   ```

## Project Purpose

This project demonstrates the practical application of RFID-based access control, database storage, messaging between system components, and web-based monitoring.

## Author

Sharvin Kumar

Bachelor of Computer Science (Hons)
