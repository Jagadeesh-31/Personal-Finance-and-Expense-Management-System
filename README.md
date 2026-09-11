# 💼 Personal Finance Management System

A comprehensive Python and Streamlit web application for tracking income & expenses, managing monthly budgets, visualizing financial data with interactive Plotly graphs & pie charts, and automating WhatsApp & email report delivery.

---

## ✨ Features

### 📊 Interactive Visual Analytics & Charts (Plotly)
- **Financial Summary Dashboard**: 4 key KPI metric cards (*Income*, *Expense*, *Savings*, *Budget*) paired with:
  - **Financial Overview Bar Chart**: Color-coded comparison of Income, Expenses, Savings, and Budget.
  - **Income Allocation Pie Chart**: Visual breakdown of Income Spent vs Net Savings.
  - **Category Expense Pie Chart**: Interactive donut/pie chart displaying category spending shares.
  - **Daily Spending Trend Line Chart**: Tracks daily/monthly expense trajectory over time.
- **Category Wise Expense Analytics**:
  - **KPI Summary Cards**: Total Expenses, Highest Expense Category (% share), and Active Categories.
  - **Side-by-Side Visualizations**: Plotly Bar Chart (amount by category) + Donut/Pie Chart (percentage distribution).
- **Savings Goal Tracker**: Interactive target checker with a visual progress bar and remaining savings calculation.
- **Monthly Savings Visual Progress Bar**: Visual gauge meter tracking monthly savings targets.

### 🔐 User Authentication & 2FA Security
- **Secure Password Hashing**: Passwords encrypted using **PBKDF2 HMAC SHA-256** with 32-character random salts.
- **Multi-User Data Isolation**: Personalized private CSV storage directories per account.
- **Email & WhatsApp 2FA OTP Verification**: 6-digit OTP verification for email address updates and WhatsApp phone number changes.
- **Profile Picture Management**: Upload custom profile avatars (PNG, JPG, WEBP).

### 📲 WhatsApp & Email Automated Delivery
- **Interactive WhatsApp Web Sharing (100% Free)**: One-click pre-filled WhatsApp Web link dispatch (`wa.me`).
- **Meta WhatsApp Cloud API**: Automated direct background message delivery.
- **Automated Monthly Scheduler**: `monthly_scheduler.py` background worker for automated dispatch.
- **Email Report Delivery**: Automated financial breakdown reports dispatched to registered email addresses.

### 📊 Data Management & Reports
- **Interactive Data Editors**: Modify income, expenses, and budgets in real time via Streamlit `st.data_editor`.
- **Multi-Sheet Excel Export**: Generates `.xlsx` reports with separate sheets for *Income*, *Expenses*, *Budget*, *Transactions*, *Category Expenses*, and *Summary*.
- **Keyword Search & Row Deletion**: Search transactions across all fields or safely delete entries.
- **Automated PyTest Suite**: 33 unit tests covering finance logic, authentication, OTP security, WhatsApp service, and logging.

---

## 🛠️ Technology Stack

- **Frontend & App Framework**: Streamlit
- **Visualizations & Charts**: Plotly Express & Plotly Graph Objects
- **Data Processing**: Pandas
- **Export Engine**: OpenPyXL (Excel)
- **Authentication & Security**: PBKDF2 HMAC SHA-256
- **Automated Testing**: PyTest

---

## 💻 Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/jagadeesh-boyalla-03/Personal-Finance-and-Expense-Management-System.git
   cd Personal-Finance-and-Expense-Management-System
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables (Optional for Meta API & Email)**:
   Copy `.env.example` to `.env` and fill in your details:
   ```env
   META_WHATSAPP_TOKEN=your_meta_token_here
   META_PHONE_NUMBER_ID=your_meta_phone_number_id_here
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

---

## 🚀 Running the Application

### Launch Streamlit Dashboard (Recommended)
```bash
streamlit run streamlit_app.py
```

### Run Console Terminal App
```bash
python main.py
```

### Run Desktop GUI App (Tkinter)
```bash
python gui/gui_app.py
```

### Run Automated Monthly WhatsApp Scheduler
```bash
python monthly_scheduler.py
```

---

## 🧪 Running Automated Tests

Run the complete 33-test PyTest suite:
```bash
python -m pytest
```

---

## 📁 Project Architecture

```text
├── streamlit_app.py       # Main Streamlit Web Application with Plotly Charts
├── auth.py                # User Authentication & 2FA OTP Management
├── finance.py             # Core Finance Data Engine & CSV Storage
├── email_service.py       # Email Delivery Engine (SMTP)
├── whatsapp_service.py    # WhatsApp Web Link & Meta Cloud API Dispatcher
├── monthly_scheduler.py   # Background Monthly Automated Dispatcher
├── logger_config.py       # Logging Configuration & Rotating File Handlers
├── main.py                # Console Terminal Entry Point
├── gui/
│   └── gui_app.py         # Tkinter Offline Desktop Application
├── tests/                 # Automated PyTest Test Suite (33 Tests)
│   ├── test_auth.py
│   ├── test_finance.py
│   ├── test_profile_otp.py
│   ├── test_whatsapp.py
│   ├── test_report.py
│   └── test_logger.py
├── requirements.txt       # Python Dependencies
└── README.md              # Project Documentation
```

---

## 📄 License
This project is open-source and available under the MIT License.
