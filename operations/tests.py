from datetime import date
from decimal import Decimal
from django.test import TestCase

from operations.models import (
    AttendanceLog,
    DowntimeLog,
    Employee,
    EquipmentCategory,
    InventoryItem,
    InventoryMonthlyBalance,
    MachineLine,
    OvertimeRecord,
)
from operations.services.analytics import get_monthly_report_data


class AnalyticsServiceTests(TestCase):
    """Verifies Pandas monthly aggregations for Attendance, Overtime, Inventory, and Downtime."""

    def setUp(self):
        # 1. Employees
        self.emp1 = Employee.objects.create(
            employee_id="EMP-101",
            full_name="Juan Dela Cruz",
            role="Operator",
            team_group="YB",
        )
        self.emp2 = Employee.objects.create(
            employee_id="EMP-102",
            full_name="Pedro Santos",
            role="Technician",
            team_group="YB",
        )

        # 2. Attendance Logs (January 2026)
        AttendanceLog.objects.create(
            employee=self.emp1,
            date=date(2026, 1, 5),
            leave_code=AttendanceLog.LeaveCode.VL,
        )
        AttendanceLog.objects.create(
            employee=self.emp1,
            date=date(2026, 1, 12),
            leave_code=AttendanceLog.LeaveCode.SL,
        )
        AttendanceLog.objects.create(
            employee=self.emp2,
            date=date(2026, 1, 15),
            leave_code=AttendanceLog.LeaveCode.LATE,
        )

        # 3. Overtime Records (January 2026)
        OvertimeRecord.objects.create(
            employee=self.emp1,
            date=date(2026, 1, 10),
            hours=Decimal("4.00"),
            reason=OvertimeRecord.OvertimeReason.FILL_UP_MANNING,
        )
        OvertimeRecord.objects.create(
            employee=self.emp2,
            date=date(2026, 1, 18),
            hours=Decimal("2.50"),
            reason=OvertimeRecord.OvertimeReason.REPLACED_MOBIL_OIL_TANK,
        )

        # 4. Chemical Inventory (BIOSOL L across Jan & Feb 2026)
        self.biosol = InventoryItem.objects.create(
            name="BIOSOL L",
            packaging="200L drum",
            unit="L",
        )
        # Jan 2026 (31 days): Starting 200 + Withdrawn 400 - End 290 = 310 L (Avg daily = 10.00 L)
        InventoryMonthlyBalance.objects.create(
            item=self.biosol,
            year=2026,
            month=1,
            starting_inventory=Decimal("200.00"),
            withdrawn=Decimal("400.00"),
            end_inventory=Decimal("290.00"),
        )
        # Feb 2026 (28 days): Starting 290 + Withdrawn 200 - End 210 = 280 L (Avg daily = 10.00 L, YTD avg monthly = (310+280)/2 = 295.00 L)
        InventoryMonthlyBalance.objects.create(
            item=self.biosol,
            year=2026,
            month=2,
            starting_inventory=Decimal("290.00"),
            withdrawn=Decimal("200.00"),
            end_inventory=Decimal("210.00"),
        )

        # 5. Machine Lines & Downtime Logs (January 2026)
        self.yb1 = MachineLine.objects.create(code="YB-1")
        self.yb2 = MachineLine.objects.create(code="YB-2")
        self.feeder_orifice = EquipmentCategory.objects.create(
            category=EquipmentCategory.MainCategory.FEEDER,
            component_name="Orifice",
        )
        self.is_baffle = EquipmentCategory.objects.create(
            category=EquipmentCategory.MainCategory.IS_MACHINE,
            component_name="Baffle arm / Plate",
        )

        DowntimeLog.objects.create(
            date=date(2026, 1, 18),
            machine_line=self.yb1,
            equipment=self.is_baffle,
            duration_minutes=45,
            remarks="Sec.7 re-aligned baffle arm (01/18)",
        )
        DowntimeLog.objects.create(
            date=date(2026, 1, 20),
            machine_line=self.yb2,
            equipment=self.feeder_orifice,
            duration_minutes=75,
            remarks="Replaced orifice ring",
        )

    def test_monthly_report_aggregations(self):
        report = get_monthly_report_data(year=2026, month=1, team_group="YB")

        # Verify Attendance Matrix
        self.assertEqual(report.attendance.total_events, 3)
        emp1_row = report.attendance.matrix_df[
            report.attendance.matrix_df["employee_id"] == "EMP-101"
        ].iloc[0]
        self.assertEqual(emp1_row["VL"], 1)
        self.assertEqual(emp1_row["SL"], 1)
        self.assertEqual(emp1_row["TOTAL"], 2)

        # Verify Overtime Summary
        self.assertEqual(report.overtime.total_hours, 6.5)
        self.assertEqual(len(report.overtime.by_reason_df), 2)

        # Verify Inventory Summary (Jan 2026)
        inv_row = report.inventory.summary_df.iloc[0]
        self.assertEqual(inv_row["monthly_consumption"], 310.0)
        self.assertEqual(inv_row["average_daily_consumption"], 10.0)
        self.assertEqual(inv_row["average_monthly_consumption"], 310.0)

        # Verify YTD Rolling Average on Feb 2026
        feb_report = get_monthly_report_data(year=2026, month=2, team_group="YB")
        feb_inv_row = feb_report.inventory.summary_df.iloc[0]
        self.assertEqual(feb_inv_row["monthly_consumption"], 280.0)
        self.assertEqual(feb_inv_row["average_daily_consumption"], 10.0)
        self.assertEqual(feb_inv_row["average_monthly_consumption"], 295.0)

        # Verify Downtime Summary
        self.assertEqual(report.downtime.total_minutes, 120)
        self.assertEqual(report.downtime.total_hours, 2.0)
        feeder_row = report.downtime.by_category_df[
            report.downtime.by_category_df["category"] == "FEEDER"
        ].iloc[0]
        self.assertEqual(feeder_row["total_minutes"], 75)
        self.assertEqual(feeder_row["percentage"], 62.5)
