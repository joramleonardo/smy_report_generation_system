# 🏭 SMY Plant Report Generation System
### Glass Forming Department Operations & Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.1+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Tailwind CSS](https://img.shields.io/badge/Django--Unfold-Tailwind_Admin-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://github.com/unfoldadmin/django-unfold)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Engine-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Database](https://img.shields.io/badge/MySQL%20%7C%20SQLite-Dual_Engine-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)

---

## 📖 Overview

The **SMY Plant Report Generation System** is an enterprise operations management and reporting platform designed for the **Glass Forming Department** at **San Miguel Yamamura Packaging Corporation (SMY Glass Plant)**.

It transitions manual, fragmented Google Sheets and Excel logbooks into a unified, automated, and secure digital platform. The system empowers shift leaders, technicians, and plant supervisors to track shift attendance, monitor high-value chemical consumables, record equipment downtime, and generate operational analytics with corporate-standard reporting.

---

## ✨ Key Features & Operational Modules

### 1. 👥 Attendance & Overtime Tracking
* **Comprehensive Shift Leave Tracking:** Real-time logging of plant-specific leave codes (`VL`, `SL`, `EL`, `AWP`, `HDSL`, `PL`, `HL`, `XL`, `OPT`, `HD`, `OB`, `CS`, `UL`, `LATE`).
* **Overtime Accounting:** Detailed tracking of personnel overtime hours mapped to operational work orders (*TL report, Feed forward, Wise proposal, Housekeeping, Group meeting, Holiday duty, Excess duty, Manning fill-up, Mobil oil tank replacement*).
* **Workforce Availability Analytics:** Instant visibility into group shift rosters (e.g., Team B / Group B - YB).

### 2. 🧪 Chemical & Consumables Inventory
* **BIOSOL L (200L Drum) Management:** End-to-end tracking of glass lubricant drums and dilution consumables.
* **Consumption Computations:**
  $$\text{Monthly Consumption (L)} = \text{Starting Inventory} + \text{Withdrawn} - \text{Ending Inventory}$$
* **Averages & Thresholds:** Automated computation of Average Daily Consumption (ADC) and Average Monthly Consumption (AMC) to prevent line starvation.

### 3. ⚙️ Machine Downtime & Maintenance Logs
* **Production Line Granularity:** Dedicated incident logging for lines **YB-1, YB-2, YB-3, and YB-4**.
* **Hierarchical Equipment Categorization:**
  * **FEEDER:** Plunger, Feeder Tube, Orifice, Shear Blade, Shear Mechanism, Shear Spray, Drop Guide, Biosol Pump, Gob Distributor, Weight Fluctuation, Gob Mis-delivery.
  * **I.S. MACHINE:** Trough / Deflector, Baffle Arm / Plate, Blow Head, Mold Mechanisms.
  * **WARE HANDLING:** Conveyor, Stacker, Transfer, Ware Leak.
  * **OTHERS:** Low Air Pressure, Electrical Power Failure, Normal Stop, Flexis - UC, Maintenance Stop, MCB, Hot End Coating.
* **Incident Analytics:** Duration logging in minutes paired with technician field remarks and automated Pareto / distribution bar charts.

### 4. 🎨 Modern Tailwind UI & Data Export
* **Django Unfold:** Sleek, responsive, Tailwind CSS-based admin portal optimized for tablets, workstations, and control room screens.
* **Pure Python Export Pipeline:**
  * **openpyxl:** Formatted Excel workbooks for plant audits.
  * **ReportLab:** Formatted corporate PDF monthly summary sheets.
  * **Matplotlib & Pillow:** Embedded visualization charts for downtime trends.

---

## 🏗️ Architecture & Tech Stack

```
┌────────────────────────────────────────────────────────┐
│               Web Browser / Tablet UI                  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│              DJANGO 6.x APPLICATION CORE               │
│                                                        │
│  1. Presentation & Encoding:                           │
│     • Django-Unfold (Modern Tailwind Admin Theme)      │
│     • WhiteNoise (Zero-overhead Static File Serving)   │
│                                                        │
│  2. Security & Data Layer:                             │
│     • Role-Based Access Control (RBAC)                 │
│     • Dual DB: SQLite (Dev) / MySQL (Hostinger Prod)   │
│     • PyMySQL (Pure-Python MySQL DB-API driver)        │
│                                                        │
│  3. Computation & Reporting Engine:                    │
│     • Pandas & NumPy: Fast time-series aggregations    │
│     • Matplotlib: Automated downtime bar charts        │
│     • openpyxl: Production Excel exports               │
│     • ReportLab: Department PDF summary documents      │
└────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```text
smy_report_generation_system/
├── config/                     # Core Django configuration
│   ├── settings.py             # Dual-engine settings (MySQL / SQLite + WhiteNoise)
│   ├── urls.py                 # URL routing (/admin/ redirect)
│   ├── wsgi.py                 # Standard WSGI entry
│   ├── asgi.py                 # ASGI configuration
│   └── __init__.py             # PyMySQL driver registration
├── operations/                 # Operational application
│   ├── admin.py                # Django-Unfold admin definitions & badges
│   ├── models.py               # ORM (Employee, Attendance, Inventory, Downtime)
│   ├── services/
│   │   └── analytics.py        # Pandas aggregation & calculation engine
│   ├── management/commands/
│   │   └── seed_plant_data.py  # Automated database seeding command
│   └── migrations/             # Database migration history
├── passenger_wsgi.py           # Hostinger CloudLinux/Passenger entrypoint
├── requirements.txt            # Production dependencies
├── pyproject.toml              # UV / PEP 621 package metadata
├── .env.example                # Environment variables template
├── PROJECT_SPEC.md             # Functional requirements & project specification
└── manage.py                   # Django CLI executable
```

---

## 🚀 Quickstart & Local Setup

### Prerequisites
* **Python 3.12+**
* [**uv**](https://docs.astral.sh/uv/) (recommended) or standard `pip` / `venv`

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/joramleonardo/smy_report_generation_system.git
   cd smy_report_generation_system
   ```

2. **Set up the virtual environment:**
   * Using `uv` (Fastest):
     ```bash
     uv sync
     ```
   * Using standard `pip`:
     ```bash
     python -m venv .venv
     # Windows:
     .venv\Scripts\activate
     # Linux / macOS:
     source .venv/bin/activate
     pip install -r requirements.txt
     ```

3. **Configure Environment Variables:**
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   *(For local development, leaving default values will automatically use SQLite).*

4. **Apply Migrations & Seed Sample Data:**
   ```bash
   uv run python manage.py migrate
   uv run python manage.py seed_plant_data
   ```

5. **Create a Superuser (Admin Account):**
   ```bash
   uv run python manage.py createsuperuser
   ```

6. **Start the Development Server:**
   ```bash
   uv run python manage.py runserver
   ```
   Open [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) in your browser.

---

## 🌐 Production Deployment (Hostinger)

This repository includes full out-of-the-box support for **Hostinger Python Hosting (Passenger WSGI + MySQL)**.

### Deployment Parameters
* **Subdomain:** `eoasystem.jkleonardo.tech`
* **Root Path:** `/domains/jkleonardo.tech/public_html/eoasystem`
* **Database:** MySQL (`u962919458_eoasystem`)

### Key Deployment Files
* **`passenger_wsgi.py`:** Pre-configured WSGI bridge for Passenger.
* **`WhiteNoise`:** Pre-configured in `settings.py` for serving Tailwind assets directly without complex Apache/Nginx aliases.
* **`PyMySQL`:** Pre-registered in `config/__init__.py` to eliminate binary compilation issues on shared hosting.

### Server Commands
Run in the Hostinger SSH / Terminal:
```bash
# 1. Run migrations against Hostinger MySQL
python manage.py migrate

# 2. (Optional) Seed initial plant data
python manage.py seed_plant_data

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Create admin user
python manage.py createsuperuser
```

---

## 📋 Environment Variables Reference

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | Secret cryptographic signing key | *random secure string* |
| `DJANGO_DEBUG` | Enable/disable debug mode | `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hostnames | `eoasystem.jkleonardo.tech,localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated trusted CSRF origins | `https://eoasystem.jkleonardo.tech` |
| `DB_ENGINE` | Database engine | `mysql` (production) or blank (SQLite) |
| `DB_NAME` | Database name | `u962919458_eoasystem` |
| `DB_USER` | MySQL user | `u962919458_eoasystem` |
| `DB_PASSWORD` | MySQL password | *your password* |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `3306` |

---

## 👥 Contributors & Maintainers

* **Joram Leonardo** ([@joramleonardo](https://github.com/joramleonardo))
* **San Miguel Yamamura Packaging Corporation** - SMY Glass Plant (Glass Forming Dept)

---

## 📄 License

This project is proprietary and intended for operational use at San Miguel Yamamura Packaging Corporation.
