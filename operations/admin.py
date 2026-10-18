from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import (
    AttendanceLog,
    DowntimeLog,
    Employee,
    EquipmentCategory,
    InventoryItem,
    InventoryMonthlyBalance,
    MachineLine,
    OvertimeRecord,
)


# ==============================================================================
# INLINE ADMIN CLASSES (For quick relational encoding on parent pages)
# ==============================================================================

class AttendanceLogInline(TabularInline):
    model = AttendanceLog
    extra = 1
    fields = ["date", "leave_code", "remarks"]
    tab = True


class OvertimeRecordInline(TabularInline):
    model = OvertimeRecord
    extra = 1
    fields = ["date", "hours", "reason", "remarks"]
    tab = True


class InventoryMonthlyBalanceInline(TabularInline):
    model = InventoryMonthlyBalance
    extra = 1
    fields = [
        "year",
        "month",
        "starting_inventory",
        "withdrawn",
        "end_inventory",
    ]
    tab = True


# ==============================================================================
# MODULE 1: ATTENDANCE & OVERTIME TRACKING ADMIN
# ==============================================================================

@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = [
        "employee_id",
        "full_name",
        "role",
        "team_group",
        "is_active",
        "created_at",
    ]
    list_filter = ["team_group", "role", "is_active"]
    search_fields = ["employee_id", "full_name", "role"]
    list_editable = ["is_active"]
    inlines = [AttendanceLogInline, OvertimeRecordInline]


@admin.register(AttendanceLog)
class AttendanceLogAdmin(ModelAdmin):
    list_display = [
        "date",
        "employee",
        "display_leave_code",
        "remarks",
    ]
    list_filter = ["leave_code", "date", "employee__team_group"]
    search_fields = [
        "employee__full_name",
        "employee__employee_id",
        "remarks",
    ]
    autocomplete_fields = ["employee"]
    date_hierarchy = "date"
    list_select_related = ["employee"]

    @display(description="Leave Code", label=True)
    def display_leave_code(self, obj: AttendanceLog) -> str:
        return obj.get_leave_code_display()


@admin.register(OvertimeRecord)
class OvertimeRecordAdmin(ModelAdmin):
    list_display = [
        "date",
        "employee",
        "hours",
        "display_reason",
        "remarks",
    ]
    list_filter = ["reason", "date", "employee__team_group"]
    search_fields = [
        "employee__full_name",
        "employee__employee_id",
        "reason",
        "remarks",
    ]
    autocomplete_fields = ["employee"]
    date_hierarchy = "date"
    list_select_related = ["employee"]

    @display(description="OT Reason", label=True)
    def display_reason(self, obj: OvertimeRecord) -> str:
        return obj.reason


# ==============================================================================
# MODULE 2: CONSUMABLES / CHEMICAL INVENTORY ADMIN
# ==============================================================================

@admin.register(InventoryItem)
class InventoryItemAdmin(ModelAdmin):
    list_display = ["name", "packaging", "unit"]
    search_fields = ["name", "packaging"]
    inlines = [InventoryMonthlyBalanceInline]


@admin.register(InventoryMonthlyBalance)
class InventoryMonthlyBalanceAdmin(ModelAdmin):
    list_display = [
        "item",
        "year",
        "month",
        "starting_inventory",
        "withdrawn",
        "end_inventory",
        "display_monthly_consumption",
        "display_avg_daily",
        "display_avg_monthly",
    ]
    list_filter = ["item", "year", "month"]
    search_fields = ["item__name"]
    readonly_fields = [
        "display_monthly_consumption",
        "display_avg_daily",
        "display_avg_monthly",
        "updated_at",
    ]
    list_select_related = ["item"]

    @display(description="Monthly Consumption")
    def display_monthly_consumption(self, obj: InventoryMonthlyBalance) -> str:
        return f"{obj.monthly_consumption} {obj.item.unit}"

    @display(description="Avg Daily Consumption")
    def display_avg_daily(self, obj: InventoryMonthlyBalance) -> str:
        return f"{obj.average_daily_consumption} {obj.item.unit}/day"

    @display(description="Avg Monthly Consumption")
    def display_avg_monthly(self, obj: InventoryMonthlyBalance) -> str:
        return f"{obj.average_monthly_consumption} {obj.item.unit}/mo"


# ==============================================================================
# MODULE 3: MACHINE DOWNTIME & MAINTENANCE LOGS ADMIN
# ==============================================================================

@admin.register(MachineLine)
class MachineLineAdmin(ModelAdmin):
    list_display = ["code", "description", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["code", "description"]
    list_editable = ["is_active"]


@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(ModelAdmin):
    list_display = ["display_category", "component_name"]
    list_filter = ["category"]
    search_fields = ["category", "component_name"]

    @display(description="Main Category", label=True)
    def display_category(self, obj: EquipmentCategory) -> str:
        return obj.get_category_display()


@admin.register(DowntimeLog)
class DowntimeLogAdmin(ModelAdmin):
    list_display = [
        "date",
        "machine_line",
        "display_category",
        "equipment",
        "duration_minutes",
        "remarks",
    ]
    list_filter = [
        "machine_line",
        "equipment__category",
        "date",
    ]
    search_fields = [
        "machine_line__code",
        "equipment__component_name",
        "remarks",
    ]
    autocomplete_fields = ["machine_line", "equipment"]
    date_hierarchy = "date"
    list_select_related = ["machine_line", "equipment"]

    @display(description="Category", label=True)
    def display_category(self, obj: DowntimeLog) -> str:
        return obj.equipment.get_category_display()
