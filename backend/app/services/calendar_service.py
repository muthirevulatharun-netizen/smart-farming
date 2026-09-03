import datetime
from typing import Dict, Any, List, Optional

# Crop cycle template schedules (offset in days from sowing date)
CROP_CALENDAR_TEMPLATES = {
    "Tomato": {
        "duration_days": 130,
        "tasks": [
            {"days": -7, "stage": "Land Preparation", "task": "Deep ploughing, incorporate FYM @ 8t/acre, and prepare raised nursery beds."},
            {"days": 0, "stage": "Sowing / Nursery", "task": "Treat seeds with Trichoderma viride (4g/kg) and sow in pro-trays."},
            {"days": 25, "stage": "Transplanting", "task": "Transplant 25-day old healthy seedlings onto main field with 60x45 cm spacing."},
            {"days": 40, "stage": "Vegetative & Weeding", "task": "First manual weeding, shallow hoeing, and install bamboo/string stakes."},
            {"days": 55, "stage": "Top Dressing", "task": "Apply first split dose of Nitrogen (Urea @ 25kg/acre) and MOP @ 15kg/acre."},
            {"days": 70, "stage": "Flowering & Pest Watch", "task": "Hang yellow sticky traps for whiteflies; spray Boron (1g/L) for fruit set."},
            {"days": 85, "stage": "Fruit Development", "task": "Maintain regular drip irrigation and scout lower canopy for Early Blight."},
            {"days": 110, "stage": "First Picking", "task": "Harvest breaker-stage firm red fruits in early morning hours."},
            {"days": 130, "stage": "Final Harvest", "task": "Complete final fruit picking and clear crop residue."}
        ]
    },
    "Rice": {
        "duration_days": 125,
        "tasks": [
            {"days": -10, "stage": "Nursery Preparation", "task": "Puddle nursery bed, apply DAP @ 10kg/acre and biofertilizers."},
            {"days": 0, "stage": "Seed Sowing", "task": "Sprout paddy seeds and broadcast uniformly over wet nursery bed."},
            {"days": 22, "stage": "Main Field Puddling", "task": "Puddle main field thoroughly and level using wooden plank."},
            {"days": 25, "stage": "Transplanting", "task": "Transplant 2-3 seedlings per hill at 20x15 cm spacing."},
            {"days": 45, "stage": "Tillering & Weeding", "task": "Run conoweeder and apply first top dressing of Urea (30kg/acre) with Zinc sulphate."},
            {"days": 70, "stage": "Panicle Initiation", "task": "Maintain 2-3 cm standing water; apply second top dressing of Potash."},
            {"days": 95, "stage": "Flowering & Milking", "task": "Scout for Yellow Stem Borer; ensure field is not water-stressed."},
            {"days": 115, "stage": "Dough & Maturity", "task": "Drain field water 10 days before scheduled harvesting."},
            {"days": 125, "stage": "Harvesting", "task": "Harvest when 85% of panicle grains turn golden yellow."}
        ]
    },
    "Cotton": {
        "duration_days": 160,
        "tasks": [
            {"days": -15, "stage": "Field Prep", "task": "Deep subsoiling to break hardpan; apply neem cake @ 200kg/acre."},
            {"days": 0, "stage": "Sowing", "task": "Dibble delinted seeds on ridges at 90x60 cm spacing under moist soil."},
            {"days": 20, "stage": "Thinning & Gap Filling", "task": "Retain one vigorous seedling per hill and fill missing gaps."},
            {"days": 45, "stage": "Square Formation", "task": "First top dressing of Nitrogen; install pheromone traps for bollworms."},
            {"days": 75, "stage": "Flowering", "task": "Spray Planofix (NAA) @ 4ml/15L to prevent flower and square shedding."},
            {"days": 105, "stage": "Boll Development", "task": "Inspect bolls for pink bollworm entry; spray 13:00:45 (Potassium Nitrate 1%)."},
            {"days": 140, "stage": "First Burst Picking", "task": "Pick clean, fully opened fluffy white bolls after dew dries."},
            {"days": 160, "stage": "Final Picking", "task": "Complete picking and shred cotton stalks with tractor rotavator."}
        ]
    }
}

class CalendarService:
    @classmethod
    def generate_schedule(cls, crop: str, sowing_date: datetime.date, location: Optional[str] = None) -> Dict[str, Any]:
        crop_key = crop.capitalize()
        template = CROP_CALENDAR_TEMPLATES.get(crop_key, CROP_CALENDAR_TEMPLATES["Tomato"])

        sowing_dt = datetime.datetime.combine(sowing_date, datetime.time.min)
        total_duration = template["duration_days"]
        harvest_dt = sowing_dt + datetime.timedelta(days=total_duration)

        tasks_list = []
        for i, t in enumerate(template["tasks"]):
            t_date = sowing_dt + datetime.timedelta(days=t["days"])
            tasks_list.append({
                "id": i + 1,
                "crop": crop_key,
                "stage": t["stage"],
                "task": t["task"],
                "recommended_date": t_date.strftime("%Y-%m-%d"),
                "status": "completed" if t_date.date() < datetime.date.today() else "pending"
            })

        return {
            "success": True,
            "crop": crop_key,
            "sowing_date": sowing_dt.strftime("%Y-%m-%d"),
            "estimated_harvest_date": harvest_dt.strftime("%Y-%m-%d"),
            "total_duration_days": total_duration,
            "tasks": tasks_list
        }

calendar_service = CalendarService()
