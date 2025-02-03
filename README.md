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
- SQLite3 (comes pre-installed with Python)

## Installation and Setup

1. Clone the repository or download the source code:
   \`\`\`
   git clone https://github.com/your-username/clothing-store-db.git
   cd clothing-store-db
   \`\`\`

2. Create and activate a virtual environment (recommended):
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   \`\`\`

3. Install the required dependencies:
   \`\`\`
   pip install pillow pycryptodome
   \`\`\`

4. Set up the configuration:
   - Open the `config.py` file.
   - Review and modify the settings if necessary, such as the database name or encryption key.
   - Save the changes.

5. Initialize the database:
   - The database will be automatically created when you first run the application.
   - Ensure you have write permissions in the project directory.

## Running the Application

1. Ensure you're in the project directory and your virtual environment is activated.

2. Run the main application script:
   \`\`\`
   python clothing_store_db.py
   \`\`\`

3. The application will launch, displaying the main window with various tabs for different functionalities.

4. If it's the first time running the application, it will automatically create and initialize the SQLite database.

## Using the Application

1. **Inventory Management**:
   - Use the "Add Item" tab to add new items to the inventory.
   - Fill in all required fields (name, category, price, size, quantity).
   - Optionally, add an image for the item.
   - Click "Add Item" to save the new item to the database.
   - Use the "Inventory" tab to view all items and search for specific ones.
   - Double-click on an item in the inventory list to view or edit its details.

2. **Sales Management**:
   - The "Sales Report" tab shows recent sales transactions.
   - Use the "Refresh" button to update the sales data.
   - Click "Export Report" to save the sales report as a text file.

3. **Customer Management**:
   - Navigate to the "Customers" tab to manage customer information.
   - Use the "Add Customer" button to add new customers.
   - Search for customers using the search bar at the top of the tab.

4. **Employee Management**:
   - The "Employees" tab allows you to manage employee records.
   - Add new employees by clicking the "Add Employee" button.
   - View and search for employee information in the employee list.

## Database Information

- The application uses SQLite, a serverless database engine.
- Database file: `clothing_store.db` (created in the same directory as the application).
- Tables are automatically created on first run:
  - `inventory`: Stores item details
  - `inventory_sizes`: Manages sizes and quantities for inventory items
  - `item_images`: Stores images for inventory items
  - `sales`: Records sales transactions
  - `customers`: Stores customer information
  - `employees`: Manages employee records
- Data is automatically saved to the database as you use the application.
- No additional database setup or configuration is required.

## Troubleshooting

- **Application doesn't start**: 
  - Ensure all dependencies are installed correctly.
  - Check if Python is in your system PATH.

- **Database errors**: 
  - Verify you have write permissions in the application directory.
  - Check the `clothing_store.log` file for specific error messages.

- **Images not displaying**: 
  - Ensure the Pillow library is installed correctly.
  - Verify the image file exists and is in a supported format (PNG, JPEG, GIF).

- **Encryption issues**: 
  - Check if the pycryptodome library is installed correctly.
  - Ensure the SECRET_KEY in `config.py` hasn't been modified unexpectedly.

- **Performance issues**: 
  - For large databases, operations might slow down. Consider optimizing queries or indexing if this becomes a problem.

If problems persist, check the application logs for more detailed error messages, and consider reporting the issue on the project's issue tracker.

