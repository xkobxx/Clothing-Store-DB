# Clothing Store Database Management System

## Overview

This Clothing Store Database Management System is a comprehensive solution for managing inventory, sales, customers, and employees in a clothing retail environment. Built with Python and Tkinter, it provides a user-friendly graphical interface for efficient data management and reporting.

## Features

- **Inventory Management**: Add, update, and delete clothing items with details such as name, category, price, size, quantity, and color.
- **Sales Tracking**: Record and view sales transactions.
- **Customer Management**: Maintain a database of customer information.
- **Employee Management**: Keep track of employee details including positions and salaries.
- **Reporting**: Generate and export sales reports.
- **Data Encryption**: Secure storage of sensitive information using AES encryption.
- **Image Support**: Store and display product images.
- **Search Functionality**: Quick search capabilities for inventory, customers, and employees.

## Requirements

- Python 3.x
- Tkinter (usually comes pre-installed with Python)
- Pillow (PIL Fork) for image processing
- pycryptodome for encryption

## Installation and Setup

1. Clone the repository or download the source code.

2. Install the required dependencies:
   \`\`\`
   pip install pillow pycryptodome
   \`\`\`

   If you're using a virtual environment (recommended), set it up first:
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install pillow pycryptodome
   \`\`\`

3. Set up the SQLite database:
   - The application will automatically create the necessary database file and tables on first run.
   - Ensure you have write permissions in the directory where the script is located.

