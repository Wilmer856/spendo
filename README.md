# Spendo - Personal Expense Tracker

Spendo is a **personal finance management web application** designed to help users **track their expenses, analyze spending habits, and manage their financial goals.** With interactive reports, category-based tracking, and a user-friendly dashboard, Spendo simplifies budgeting and financial planning.

## Features

- **User Authentication** – Secure user registration, login, and profile management.
- **Expense & Income Tracking** – Add, edit, delete, and categorize transactions.
- **Data Visualization** – Graphs and reports for spending trends, category analysis, and income vs. expenses.
- **Advanced Filters** – Search transactions by category, date, and amount.
- **Downloadable Reports** – Export transaction reports and spending analytics as CSV or ZIP files.
- **Monthly Overview** – Track current balance, total income, and total expenses for the month.
- **Responsive Design** – Works seamlessly across desktop and mobile devices.
- **Account Management** – Users can update profiles, change passwords, and delete accounts securely.

## Tech Stack

- **Frontend:** Bootstrap, HTML, CSS
- **Backend:** Flask (Python)
- **Database:** SQLAlchemy (PostgreSQL)
- **Visualization:** Matplotlib, Seaborn, Pandas
- **Authentication:** Flask-Login, Flask-Bcrypt

## Getting Started

### Installation
1. **Clone the repository**
   ```sh
   git clone https://github.com/yourusername/spendo.git
   cd spendo
   ```
2. **Create and activate a virtual environment**

    ***On macOS & Linux:***
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```
    ***On Windows:***
    ```sh
    python -m venv venv
    venv\Scripts\activate
    ```
3. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```
4. **Set up environment variables**

    ***Copy the .env.example file and rename it to .env:***
    ```sh
    cp .env.example .env
    ```
5. **Initialize the database**
    ```sh
    flask db upgrade
    ```
5. **Run the application**
    ```sh
    flask run
    ```
The app will be available at http://127.0.0.1:5000/.
