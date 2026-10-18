from django.core.management.base import BaseCommand
from operations.models import EquipmentCategory, InventoryItem, MachineLine


class Command(BaseCommand):
    help = "Seeds standard SMY Glass Plant reference data (Machine Lines YB-1..4, BIOSOL L, and Equipment Categories)."

    def handle(self, *args, **options):
        # 1. Seed Machine Lines (YB-1 to YB-4)
        lines = [
            ("YB-1", "Glass Forming Line YB-1"),
            ("YB-2", "Glass Forming Line YB-2"),
            ("YB-3", "Glass Forming Line YB-3"),
            ("YB-4", "Glass Forming Line YB-4"),
        ]
        for code, desc in lines:
            MachineLine.objects.get_or_create(
                code=code,
                defaults={"description": desc, "is_active": True},
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(lines)} Machine Lines (YB-1 to YB-4)."))

        # 2. Seed Consumable Inventory Item (BIOSOL L)
        InventoryItem.objects.get_or_create(
            name="BIOSOL L",
            defaults={"packaging": "200L drum", "unit": "L"},
        )
        self.stdout.write(self.style.SUCCESS("Seeded Inventory Item: BIOSOL L (200L drum)."))

        # 3. Seed Equipment Breakdown Categories & Components
        equipment_map = {
            EquipmentCategory.MainCategory.FEEDER: [
                "Feeder plunger",
                "Feeder tube",
                "Orifice",
                "Shear blade",
                "Shear mechanism",
                "Shear spray",
                "Drop guide",
                "Biosol pump",
                "Gob distributor",
                "Scoop",
                "Weight fluctuation",
                "Gob mis-delivery",
            ],
            EquipmentCategory.MainCategory.IS_MACHINE: [
                "Trough / Deflector",
                "Baffle arm / Plate",
                "Blank mold",
                "Blow mold",
                "Neck ring",
                "Invert / Revert",
                "Take out",
                "Pusher",
            ],
            EquipmentCategory.MainCategory.WARE_HANDLING: [
                "Conveyor",
                "Stacker",
                "Transfer",
                "Leak",
                "Cross conveyor",
                "Lehr loader",
            ],
            EquipmentCategory.MainCategory.OTHERS: [
                "Power failure",
                "Low air pressure",
                "Normal stop",
                "Flexis - UC",
                "Maintenance stop",
                "MCB",
                "Hot end coating",
            ],
        }

        total_components = 0
        for category, components in equipment_map.items():
            for comp in components:
                EquipmentCategory.objects.get_or_create(
                    category=category,
                    component_name=comp,
                )
                total_components += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {total_components} Equipment Category components across FEEDER, I.S. MACHINE, WARE HANDLING, and OTHERS."
            )
        )

