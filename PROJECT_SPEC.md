# Glass Forming Department - Plant Report Generation System
**San Miguel Yamamura Packaging Corporation (SMY Glass Plant)**

---

## 1. Project Background & Requirements
This system replaces manual Google Sheets / Excel files with an integrated, automated reporting platform for the Glass Forming Department (e.g., Team B / Group B - YB).

### Core Operational Modules:
1. **Attendance & Overtime Tracking:**
   - **Leave Codes:**
     - `VL`: Vacation Leave
     - `SL`: Sick Leave
     - `EL`: Emergency Leave
     - `AWP`: Absent With Permission
     - `HDSL`: Half Day Sick Leave
     - `PL`: Paternity Leave
     - `HL`: Leave on a Holiday
     - `XL`: Leave on an excess of 40 hrs in a week
     - `OPT`: Optional Leave
     - `HD`: Half Day Vacation Leave
     - `OB`: On Official Business
     - `CS`: Change Shift
     - `UL`: Union Leave
     - `LATE`: Tardiness
   - **Overtime Records:**
     - Personnel, OT Hours, and specific plant reasons (e.g., *TL report, Feed forward, Wise proposal, Housekeeping, Group meeting, Holiday duty, Excess duty, Fill up manning, Replaced mobil oil tank*).

2. **Consumables / Chemical Inventory:**
   - E.g., **BIOSOL L (200L drum) Inventory**:
     - Starting inventory (L)
     - Withdrawn (L)
     - End inventory (L)
     - Monthly consumption (L) = `Starting + Withdrawn - End`
     - Average Daily Consumption (L)
     - Average Monthly Consumption (L)

3. **Machine Downtime & Maintenance Logs:**
   - **Lines:** YB-1, YB-2, YB-3, YB-4
   - **Breakdown Categories & Components:**
     - **FEEDER:** Feeder plunger, Feeder tube, Orifice, Shear blade, Shear mechanism, Shear spray, Drop guide, Biosol pump, Gob distributor, Scoop, Weight fluctuation, Gob mis-delivery.
     - **I.S. MACHINE:** Trough / Deflector, Baffle arm / Plate, etc.
     - **WARE HANDLING:** Conveyor, stacker, transfer, leak, etc.
     - **OTHERS:** Power failure, Low air pressure, Normal stop, Flexis - UC, Maintenance stop, MCB, Hot end coating.
   - **Incident Logs:** Duration in minutes + detailed technician remarks (e.g., *"Sec.7 re-aligned baffle arm (01/18)"*, *"Low air pressure (0.08), fb to EM"*).
   - **Visual Analytics:** Downtime category distribution bar charts (Feeder vs. I.S. Machine vs. Ware Handling vs. Others).

---

## 2. Tech Stack Architecture (Pure Python)

```
┌────────────────────────────────────────────────────────┐
│               Web Browser / Tablet UI                  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│              DJANGO 5.x / 6.x MONOLITH                 │
│                                                        │
│  1. Encoding UI:                                       │
│     • Django-Unfold (Modern Tailwind CSS Admin)        │
│                                                        │
│  2. Data & Security:                                   │
│     • Role-based Access (Operators, Supervisors)       │
│     • SQLite (Local) / PostgreSQL (Production)         │
│                                                        │
│  3. Analytics & Export Engine:                         │
│     • Pandas & NumPy: Formulations & aggregations      │
│     • Matplotlib & Pillow: Automated bar charts        │
│     • openpyxl: Excel upload & export                  │
│     • ReportLab: Corporate PDF report generation       │
└────────────────────────────────────────────────────────┘
```

---

## 3. Environment & Setup Details
- **Project Location:** `D:\Projects\Personal Projects\Report Generation System`
- **Python Version:** 3.12 (managed via `uv`)
- **Key Installed Packages:**
  - `django`
  - `django-unfold`
  - `pandas`
  - `numpy`
  - `openpyxl`
  - `matplotlib`
  - `pillow`
  - `reportlab`

### Common Commands:
* Run Development Server:
  ```bash
  uv run python manage.py runserver
  ```
* Run Database Migrations:
  ```bash
  uv run python manage.py migrate
  ```
* Create Superuser (Admin account):
  ```bash
  uv run python manage.py createsuperuser
  ```
* System Health Check:
  ```bash
  uv run python manage.py check
  ```

---

## 4. Implementation Roadmap
- [x] **Step 1:** Initialize project environment and install pure Python stack dependencies.
- [x] **Step 2:** Define Django ORM models (`Employee`, `AttendanceLog`, `OvertimeRecord`, `InventoryItem`, `InventoryMonthlyBalance`, `MachineLine`, `EquipmentCategory`, `DowntimeLog`).
- [x] **Step 3:** Register models in `operations/admin.py` with `django-unfold` for daily/monthly encoding.
- [x] **Step 4:** Implement Pandas aggregation service for monthly summary calculations.
- [ ] **Step 5:** Build Matplotlib downtime bar chart generator.
- [ ] **Step 6:** Build PDF and Excel report export views.
