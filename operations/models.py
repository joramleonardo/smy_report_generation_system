import calendar
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, F


# ==============================================================================
# MODULE 1: ATTENDANCE & OVERTIME TRACKING
# ==============================================================================

class Employee(models.Model):
    """Represents a plant personnel member in the Glass Forming Department."""

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique company ID / badge number (e.g., EMP-001).",
    )
    full_name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=100,
        default="Operator",
        help_text="Job title (e.g., Operator, Technician, Supervisor, Team Leader).",
    )
    team_group = models.CharField(
        max_length=50,
        default="YB",
        help_text="Assigned shift/group (e.g., Group B / YB).",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self) -> str:
        return f"{self.full_name} ({self.employee_id})"


class AttendanceLog(models.Model):
    """Tracks daily employee leave codes and tardiness."""

    class LeaveCode(models.TextChoices):
        VL = "VL", "VL - Vacation Leave"
        SL = "SL", "SL - Sick Leave"
        EL = "EL", "EL - Emergency Leave"
        AWP = "AWP", "AWP - Absent With Permission"
        HDSL = "HDSL", "HDSL - Half Day Sick Leave"
        PL = "PL", "PL - Paternity Leave"
        HL = "HL", "HL - Leave on a Holiday"
        XL = "XL", "XL - Leave on Excess of 40 hrs/week"
        OPT = "OPT", "OPT - Optional Leave"
        HD = "HD", "HD - Half Day Vacation Leave"
        OB = "OB", "OB - On Official Business"
        CS = "CS", "CS - Change Shift"
        UL = "UL", "UL - Union Leave"
        LATE = "LATE", "LATE - Tardiness"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_logs",
    )
    date = models.DateField()
    leave_code = models.CharField(
        max_length=10,
        choices=LeaveCode.choices,
    )
    remarks = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "employee__full_name"]
        unique_together = ["employee", "date", "leave_code"]
        verbose_name = "Attendance / Leave Log"
        verbose_name_plural = "Attendance / Leave Logs"

    def __str__(self) -> str:
        return f"{self.date} | {self.employee.full_name} - {self.leave_code}"


class OvertimeRecord(models.Model):
    """Tracks employee overtime hours and specific plant reasons."""

    class OvertimeReason(models.TextChoices):
        TL_REPORT = "TL report", "TL report"
        FEED_FORWARD = "Feed forward", "Feed forward"
        WISE_PROPOSAL = "Wise proposal", "Wise proposal"
        HOUSEKEEPING = "Housekeeping", "Housekeeping"
        GROUP_MEETING = "Group meeting", "Group meeting"
        HOLIDAY_DUTY = "Holiday duty", "Holiday duty"
        EXCESS_DUTY = "Excess duty", "Excess duty"
        FILL_UP_MANNING = "Fill up manning", "Fill up manning"
        REPLACED_MOBIL_OIL_TANK = "Replaced mobil oil tank", "Replaced mobil oil tank"
        OTHER = "Other", "Other (specify in remarks)"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="overtime_records",
    )
    date = models.DateField()
    hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.25"))],
        help_text="Overtime duration in hours (e.g., 2.50).",
    )
    reason = models.CharField(
        max_length=100,
        choices=OvertimeReason.choices,
        default=OvertimeReason.FILL_UP_MANNING,
    )
    remarks = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "employee__full_name"]
        verbose_name = "Overtime Record"
        verbose_name_plural = "Overtime Records"

    def __str__(self) -> str:
        return f"{self.date} | {self.employee.full_name} ({self.hours} hrs - {self.reason})"


# ==============================================================================
# MODULE 2: CONSUMABLES / CHEMICAL INVENTORY
# ==============================================================================

class InventoryItem(models.Model):
    """Represents a tracked plant chemical or consumable (e.g., BIOSOL L)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Chemical/consumable name (e.g., BIOSOL L).",
    )
    packaging = models.CharField(
        max_length=100,
        default="200L drum",
        help_text="Standard packaging (e.g., 200L drum).",
    )
    unit = models.CharField(
        max_length=20,
        default="L",
        help_text="Unit of measurement (e.g., L for Liters).",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"

    def __str__(self) -> str:
        return f"{self.name} ({self.packaging})"


class InventoryMonthlyBalance(models.Model):
    """Monthly inventory balance and consumption computation for a consumable."""

    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="monthly_balances",
    )
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2100)],
    )
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Month number (1 = January, 12 = December).",
    )
    starting_inventory = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Starting inventory in Liters (L).",
    )
    withdrawn = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Quantity withdrawn during the month in Liters (L).",
    )
    end_inventory = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Ending inventory at month close in Liters (L).",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-year", "-month", "item__name"]
        unique_together = ["item", "year", "month"]
        verbose_name = "Inventory Monthly Balance"
        verbose_name_plural = "Inventory Monthly Balances"

    @property
    def monthly_consumption(self) -> Decimal:
        """Formula: Starting + Withdrawn - End"""
        return (self.starting_inventory + self.withdrawn) - self.end_inventory

    @property
    def days_in_month(self) -> int:
        """Returns exact number of calendar days in the given year and month."""
        return calendar.monthrange(self.year, self.month)[1]

    @property
    def average_daily_consumption(self) -> Decimal:
        """Formula: Monthly Consumption / Days in Month"""
        days = Decimal(str(self.days_in_month))
        return (self.monthly_consumption / days).quantize(Decimal("0.01"))

    @property
    def average_monthly_consumption(self) -> Decimal:
        """Rolling average monthly consumption across recorded months for this item in the same year."""
        agg = InventoryMonthlyBalance.objects.filter(
            item=self.item,
            year=self.year,
            month__lte=self.month,
        ).aggregate(
            avg_consumption=Avg(
                F("starting_inventory") + F("withdrawn") - F("end_inventory")
            )
        )
        val = agg["avg_consumption"]
        if val is None:
            return self.monthly_consumption
        return Decimal(str(val)).quantize(Decimal("0.01"))

    def __str__(self) -> str:
        return f"{self.item.name} ({self.year}-{self.month:02d}): {self.monthly_consumption} {self.item.unit}"


# ==============================================================================
# MODULE 3: MACHINE DOWNTIME & MAINTENANCE LOGS
# ==============================================================================

class MachineLine(models.Model):
    """Represents a glass forming production line (YB-1, YB-2, YB-3, YB-4)."""

    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Line code (e.g., YB-1, YB-2, YB-3, YB-4).",
    )
    description = models.CharField(max_length=150, blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Machine Line"
        verbose_name_plural = "Machine Lines"

    def __str__(self) -> str:
        return self.code


class EquipmentCategory(models.Model):
    """Breakdown categories (Feeder, I.S. Machine, Ware Handling, Others) and components."""

    class MainCategory(models.TextChoices):
        FEEDER = "FEEDER", "Feeder"
        IS_MACHINE = "I.S. MACHINE", "I.S. Machine"
        WARE_HANDLING = "WARE HANDLING", "Ware Handling"
        OTHERS = "OTHERS", "Others"

    category = models.CharField(
        max_length=30,
        choices=MainCategory.choices,
    )
    component_name = models.CharField(
        max_length=100,
        help_text="Specific part/issue (e.g., Feeder plunger, Orifice, Baffle arm / Plate, Low air pressure).",
    )

    class Meta:
        ordering = ["category", "component_name"]
        unique_together = ["category", "component_name"]
        verbose_name = "Equipment Category & Component"
        verbose_name_plural = "Equipment Categories & Components"

    def __str__(self) -> str:
        return f"[{self.category}] {self.component_name}"


class DowntimeLog(models.Model):
    """Records individual machine breakdown/downtime incidents and technician remarks."""

    date = models.DateField()
    machine_line = models.ForeignKey(
        MachineLine,
        on_delete=models.CASCADE,
        related_name="downtime_logs",
    )
    equipment = models.ForeignKey(
        EquipmentCategory,
        on_delete=models.PROTECT,
        related_name="downtime_logs",
    )
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total downtime duration in minutes.",
    )
    remarks = models.TextField(
        help_text="Detailed technician remarks (e.g., 'Sec.7 re-aligned baffle arm (01/18)').",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "machine_line__code"]
        verbose_name = "Downtime Log"
        verbose_name_plural = "Downtime Logs"

    def __str__(self) -> str:
        return f"{self.date} | {self.machine_line.code} | {self.equipment} ({self.duration_minutes} mins)"
