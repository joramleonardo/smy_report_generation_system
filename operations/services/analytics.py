import calendar
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from operations.models import (
    AttendanceLog,
    DowntimeLog,
    Employee,
    EquipmentCategory,
    InventoryMonthlyBalance,
    MachineLine,
    OvertimeRecord,
)


@dataclass
class AttendanceSummaryResult:
    matrix_df: pd.DataFrame
    code_totals_df: pd.DataFrame
    raw_logs_df: pd.DataFrame
    total_events: int


@dataclass
class OvertimeSummaryResult:
    by_employee_df: pd.DataFrame
    by_reason_df: pd.DataFrame
    records_df: pd.DataFrame
    total_hours: float


@dataclass
class InventorySummaryResult:
    summary_df: pd.DataFrame
    total_consumed_liters: float


@dataclass
class DowntimeSummaryResult:
    by_category_df: pd.DataFrame
    line_category_matrix_df: pd.DataFrame
    by_component_df: pd.DataFrame
    logs_df: pd.DataFrame
    total_minutes: int
    total_hours: float


@dataclass
class MonthlyReportData:
    year: int
    month: int
    month_name: str
    team_group: Optional[str]
    attendance: AttendanceSummaryResult
    overtime: OvertimeSummaryResult
    inventory: InventorySummaryResult
    downtime: DowntimeSummaryResult


# ==============================================================================
# 1. ATTENDANCE & LEAVE AGGREGATION
# ==============================================================================

def get_attendance_summary(
    year: int,
    month: int,
    team_group: Optional[str] = None,
) -> AttendanceSummaryResult:
    """
    Computes a monthly Attendance / Leave matrix using Pandas.
    Rows = Active Employees; Columns = All 14 Leave Codes + TOTAL.
    """
    leave_codes = [choice[0] for choice in AttendanceLog.LeaveCode.choices]
    leave_labels = dict(AttendanceLog.LeaveCode.choices)

    emp_qs = Employee.objects.filter(is_active=True)
    if team_group:
        emp_qs = emp_qs.filter(team_group=team_group)

    employees_data = list(
        emp_qs.values("id", "employee_id", "full_name", "role", "team_group")
    )

    log_qs = AttendanceLog.objects.filter(
        date__year=year,
        date__month=month,
        employee__is_active=True,
    )
    if team_group:
        log_qs = log_qs.filter(employee__team_group=team_group)

    logs_data = list(
        log_qs.select_related("employee").values(
            "date",
            "employee_id",
            "employee__employee_id",
            "employee__full_name",
            "employee__team_group",
            "leave_code",
            "remarks",
        )
    )

    # Build raw logs DataFrame
    if logs_data:
        raw_logs_df = pd.DataFrame(logs_data).rename(
            columns={
                "employee__employee_id": "badge_id",
                "employee__full_name": "full_name",
                "employee__team_group": "team_group",
            }
        )
        raw_logs_df["leave_description"] = raw_logs_df["leave_code"].map(leave_labels)
    else:
        raw_logs_df = pd.DataFrame(
            columns=[
                "date",
                "employee_id",
                "badge_id",
                "full_name",
                "team_group",
                "leave_code",
                "leave_description",
                "remarks",
            ]
        )

    # Build base employee DataFrame
    if employees_data:
        emp_df = pd.DataFrame(employees_data).rename(columns={"id": "emp_pk"})
    else:
        emp_df = pd.DataFrame(
            columns=["emp_pk", "employee_id", "full_name", "role", "team_group"]
        )

    # Pivot leave counts per employee across all 14 leave codes
    if not raw_logs_df.empty and not emp_df.empty:
        pivot_df = pd.crosstab(
            index=raw_logs_df["employee_id"],
            columns=raw_logs_df["leave_code"],
        )
        pivot_df = pivot_df.reindex(columns=leave_codes, fill_value=0)
        matrix_df = emp_df.merge(
            pivot_df,
            left_on="emp_pk",
            right_index=True,
            how="left",
        )
        matrix_df[leave_codes] = matrix_df[leave_codes].fillna(0).astype(int)
    else:
        matrix_df = emp_df.copy()
        for code in leave_codes:
            matrix_df[code] = 0

    if not matrix_df.empty:
        matrix_df["TOTAL"] = matrix_df[leave_codes].sum(axis=1)
        matrix_df = matrix_df.drop(columns=["emp_pk"])
    else:
        matrix_df = pd.DataFrame(
            columns=["employee_id", "full_name", "role", "team_group", *leave_codes, "TOTAL"]
        )

    # Compute column totals per leave code
    code_counts = (
        matrix_df[leave_codes].sum(axis=0)
        if not matrix_df.empty
        else pd.Series(0, index=leave_codes)
    )
    code_totals_df = pd.DataFrame(
        {
            "leave_code": leave_codes,
            "description": [leave_labels[c] for c in leave_codes],
            "count": [int(code_counts.get(c, 0)) for c in leave_codes],
        }
    )

    total_events = int(code_totals_df["count"].sum())
    return AttendanceSummaryResult(
        matrix_df=matrix_df,
        code_totals_df=code_totals_df,
        raw_logs_df=raw_logs_df,
        total_events=total_events,
    )


# ==============================================================================
# 2. OVERTIME AGGREGATION
# ==============================================================================

def get_overtime_summary(
    year: int,
    month: int,
    team_group: Optional[str] = None,
) -> OvertimeSummaryResult:
    """
    Aggregates monthly Overtime hours by employee and by plant reason using Pandas.
    """
    ot_qs = OvertimeRecord.objects.filter(
        date__year=year,
        date__month=month,
    ).select_related("employee")

    if team_group:
        ot_qs = ot_qs.filter(employee__team_group=team_group)

    ot_data = list(
        ot_qs.values(
            "date",
            "employee__employee_id",
            "employee__full_name",
            "employee__role",
            "employee__team_group",
            "hours",
            "reason",
            "remarks",
        )
    )

    if not ot_data:
        empty_records = pd.DataFrame(
            columns=[
                "date",
                "employee_id",
                "full_name",
                "role",
                "team_group",
                "hours",
                "reason",
                "remarks",
            ]
        )
        empty_by_emp = pd.DataFrame(
            columns=["employee_id", "full_name", "role", "team_group", "ot_count", "total_hours"]
        )
        empty_by_reason = pd.DataFrame(
            columns=["reason", "incident_count", "total_hours", "percentage"]
        )
        return OvertimeSummaryResult(
            by_employee_df=empty_by_emp,
            by_reason_df=empty_by_reason,
            records_df=empty_records,
            total_hours=0.0,
        )

    records_df = pd.DataFrame(ot_data).rename(
        columns={
            "employee__employee_id": "employee_id",
            "employee__full_name": "full_name",
            "employee__role": "role",
            "employee__team_group": "team_group",
        }
    )
    records_df["hours"] = records_df["hours"].astype(float)

    # Group by employee
    by_employee_df = (
        records_df.groupby(
            ["employee_id", "full_name", "role", "team_group"],
            as_index=False,
        )
        .agg(
            ot_count=("hours", "count"),
            total_hours=("hours", "sum"),
        )
        .sort_values(by=["total_hours", "full_name"], ascending=[False, True])
        .reset_index(drop=True)
    )
    by_employee_df["total_hours"] = by_employee_df["total_hours"].round(2)

    # Group by plant overtime reason
    total_hours = float(records_df["hours"].sum().round(2))
    by_reason_df = (
        records_df.groupby("reason", as_index=False)
        .agg(
            incident_count=("hours", "count"),
            total_hours=("hours", "sum"),
        )
        .sort_values(by="total_hours", ascending=False)
        .reset_index(drop=True)
    )
    by_reason_df["total_hours"] = by_reason_df["total_hours"].round(2)
    by_reason_df["percentage"] = np.where(
        total_hours > 0,
        ((by_reason_df["total_hours"] / total_hours) * 100.0).round(2),
        0.0,
    )

    return OvertimeSummaryResult(
        by_employee_df=by_employee_df,
        by_reason_df=by_reason_df,
        records_df=records_df,
        total_hours=total_hours,
    )


# ==============================================================================
# 3. CONSUMABLES / CHEMICAL INVENTORY AGGREGATION
# ==============================================================================

def get_inventory_summary(year: int, month: int) -> InventorySummaryResult:
    """
    Computes monthly chemical consumption (Starting + Withdrawn - End),
    average daily consumption, and year-to-date rolling monthly average in Pandas.
    """
    ytd_qs = InventoryMonthlyBalance.objects.filter(
        year=year,
        month__lte=month,
    ).select_related("item")

    ytd_data = list(
        ytd_qs.values(
            "item_id",
            "item__name",
            "item__packaging",
            "item__unit",
            "year",
            "month",
            "starting_inventory",
            "withdrawn",
            "end_inventory",
        )
    )

    columns = [
        "item_name",
        "packaging",
        "unit",
        "year",
        "month",
        "days_in_month",
        "starting_inventory",
        "withdrawn",
        "end_inventory",
        "monthly_consumption",
        "average_daily_consumption",
        "average_monthly_consumption",
    ]

    if not ytd_data:
        return InventorySummaryResult(
            summary_df=pd.DataFrame(columns=columns),
            total_consumed_liters=0.0,
        )

    df = pd.DataFrame(ytd_data).rename(
        columns={
            "item__name": "item_name",
            "item__packaging": "packaging",
            "item__unit": "unit",
        }
    )

    for col in ["starting_inventory", "withdrawn", "end_inventory"]:
        df[col] = df[col].astype(float)

    # Formula: Monthly consumption = Starting + Withdrawn - End
    df["monthly_consumption"] = (
        df["starting_inventory"] + df["withdrawn"] - df["end_inventory"]
    ).round(2)

    # Compute rolling YTD average monthly consumption per item up to `month`
    ytd_avg_series = (
        df.groupby("item_id")["monthly_consumption"]
        .mean()
        .round(2)
        .rename("average_monthly_consumption")
    )

    # Filter down to the requested target month
    month_df = df[df["month"] == month].copy()
    if month_df.empty:
        return InventorySummaryResult(
            summary_df=pd.DataFrame(columns=columns),
            total_consumed_liters=0.0,
        )

    days_in_target_month = calendar.monthrange(year, month)[1]
    month_df["days_in_month"] = days_in_target_month
    month_df["average_daily_consumption"] = (
        month_df["monthly_consumption"] / float(days_in_target_month)
    ).round(2)

    month_df = month_df.merge(ytd_avg_series, on="item_id", how="left")
    summary_df = (
        month_df[columns]
        .sort_values(by="item_name")
        .reset_index(drop=True)
    )

    total_consumed = float(summary_df["monthly_consumption"].sum().round(2))
    return InventorySummaryResult(
        summary_df=summary_df,
        total_consumed_liters=total_consumed,
    )


# ==============================================================================
# 4. MACHINE DOWNTIME & MAINTENANCE AGGREGATION
# ==============================================================================

def get_downtime_summary(year: int, month: int) -> DowntimeSummaryResult:
    """
    Aggregates machine downtime logs across lines (YB-1..YB-4) and main categories
    (FEEDER, I.S. MACHINE, WARE HANDLING, OTHERS) using Pandas.
    """
    categories = [choice[0] for choice in EquipmentCategory.MainCategory.choices]
    category_labels = dict(EquipmentCategory.MainCategory.choices)

    active_lines = list(
        MachineLine.objects.filter(is_active=True)
        .order_by("code")
        .values_list("code", flat=True)
    )
    if not active_lines:
        active_lines = ["YB-1", "YB-2", "YB-3", "YB-4"]

    logs_qs = DowntimeLog.objects.filter(
        date__year=year,
        date__month=month,
    ).select_related("machine_line", "equipment")

    logs_data = list(
        logs_qs.values(
            "date",
            "machine_line__code",
            "equipment__category",
            "equipment__component_name",
            "duration_minutes",
            "remarks",
        )
    )

    if logs_data:
        logs_df = pd.DataFrame(logs_data).rename(
            columns={
                "machine_line__code": "line",
                "equipment__category": "category",
                "equipment__component_name": "component",
            }
        )
        logs_df["duration_minutes"] = logs_df["duration_minutes"].astype(int)
        logs_df["duration_hours"] = (logs_df["duration_minutes"] / 60.0).round(2)
    else:
        logs_df = pd.DataFrame(
            columns=[
                "date",
                "line",
                "category",
                "component",
                "duration_minutes",
                "duration_hours",
                "remarks",
            ]
        )

    total_minutes = int(logs_df["duration_minutes"].sum()) if not logs_df.empty else 0
    total_hours = round(total_minutes / 60.0, 2)

    # 1. Summary by Main Category (always includes all 4 categories in standard order)
    if not logs_df.empty:
        cat_grouped = logs_df.groupby("category").agg(
            incident_count=("duration_minutes", "count"),
            total_minutes=("duration_minutes", "sum"),
        )
        cat_grouped = cat_grouped.reindex(categories, fill_value=0).reset_index()
        cat_grouped = cat_grouped.rename(columns={"index": "category"})
    else:
        cat_grouped = pd.DataFrame(
            {
                "category": categories,
                "incident_count": [0] * len(categories),
                "total_minutes": [0] * len(categories),
            }
        )

    cat_grouped["category_label"] = cat_grouped["category"].map(category_labels)
    cat_grouped["total_hours"] = (cat_grouped["total_minutes"] / 60.0).round(2)
    cat_grouped["percentage"] = np.where(
        total_minutes > 0,
        ((cat_grouped["total_minutes"] / float(total_minutes)) * 100.0).round(2),
        0.0,
    )
    by_category_df = cat_grouped[
        [
            "category",
            "category_label",
            "incident_count",
            "total_minutes",
            "total_hours",
            "percentage",
        ]
    ]

    # 2. Line x Category Pivot Matrix (Rows: YB-1..YB-4, Columns: FEEDER, I.S. MACHINE, WARE HANDLING, OTHERS)
    if not logs_df.empty:
        pivot_matrix = pd.pivot_table(
            logs_df,
            index="line",
            columns="category",
            values="duration_minutes",
            aggfunc="sum",
            fill_value=0,
        )
        pivot_matrix = pivot_matrix.reindex(
            index=active_lines,
            columns=categories,
            fill_value=0,
        )
    else:
        pivot_matrix = pd.DataFrame(
            0,
            index=pd.Index(active_lines, name="line"),
            columns=categories,
        )

    line_category_matrix_df = pivot_matrix.reset_index()
    line_category_matrix_df["TOTAL_MINUTES"] = line_category_matrix_df[categories].sum(
        axis=1
    )
    line_category_matrix_df["TOTAL_HOURS"] = (
        line_category_matrix_df["TOTAL_MINUTES"] / 60.0
    ).round(2)

    # 3. Component-level breakdown across lines
    if not logs_df.empty:
        comp_pivot = pd.pivot_table(
            logs_df,
            index=["category", "component"],
            columns="line",
            values="duration_minutes",
            aggfunc="sum",
            fill_value=0,
        )
        comp_pivot = comp_pivot.reindex(columns=active_lines, fill_value=0)
        by_component_df = comp_pivot.reset_index()
        by_component_df["TOTAL_MINUTES"] = by_component_df[active_lines].sum(axis=1)
        by_component_df = by_component_df.sort_values(
            by=["category", "TOTAL_MINUTES"],
            ascending=[True, False],
        ).reset_index(drop=True)
    else:
        by_component_df = pd.DataFrame(
            columns=["category", "component", *active_lines, "TOTAL_MINUTES"]
        )

    return DowntimeSummaryResult(
        by_category_df=by_category_df,
        line_category_matrix_df=line_category_matrix_df,
        by_component_df=by_component_df,
        logs_df=logs_df,
        total_minutes=total_minutes,
        total_hours=total_hours,
    )


# ==============================================================================
# 5. MASTER MONTHLY REPORT AGGREGATOR
# ==============================================================================

def get_monthly_report_data(
    year: int,
    month: int,
    team_group: Optional[str] = None,
) -> MonthlyReportData:
    """
    Single entrypoint returning all aggregated Pandas DataFrames and metrics
    for the given year/month across Attendance, Overtime, Inventory, and Downtime.
    """
    month_name = calendar.month_name[month]
    return MonthlyReportData(
        year=year,
        month=month,
        month_name=month_name,
        team_group=team_group,
        attendance=get_attendance_summary(year=year, month=month, team_group=team_group),
        overtime=get_overtime_summary(year=year, month=month, team_group=team_group),
        inventory=get_inventory_summary(year=year, month=month),
        downtime=get_downtime_summary(year=year, month=month),
    )

