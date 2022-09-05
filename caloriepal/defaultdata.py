import logging
from .config import *
from .database import DBContext
from . import models


logger = logging.getLogger("backend")


def load_default_data() -> None:
    logger.info("[SYSTEM] Creating default data...")

    with DBContext() as session:

        # Create Users
        logger.info("[SYSTEM] Checking default Users.")
        user_obj = session.query(models.User).filter(models.User.username == default_user["username"]).first() # type: models.User
        if not user_obj:
            user_obj = models.User(**default_user)
            session.add(user_obj)
            session.commit()
            logger.warning(f"[SYSTEM] Created '{user_obj}'. Default username: '{default_user['username']}, Password: '{default_user['password']}'.")
        else:
            logger.debug(f"[SYSTEM] User '{user_obj}' already exists.")
        
        # Create Uoms
        logger.info("[SYSTEM] Checking Uoms.")
        for uom in uoms:
            obj = session.query(models.Uom).filter(models.Uom.name == uom["name"]).first() # type: models.Uom
            if not obj:
                obj = models.Uom(**uom)
                obj.type_name = uom["type_name"]
                session.add(obj)
                session.commit()
                logger.info(f"[SYSTEM] Created '{obj}'")
            else:
                logger.debug(f"[SYSTEM] Uom '{obj}' already exists.")
        
        # Create UomConversions
        logger.info("[SYSTEM] Checking UomConversions.")
        for uom_conversion in uom_conversions:
            from_uom_name = uom_conversion.pop("from_uom_name", None)
            to_uom_name = uom_conversion.pop("to_uom_name", None)
            from_uom = session.query(models.Uom).filter(models.Uom.name == from_uom_name).first() # type: models.Uom
            to_uom = session.query(models.Uom).filter(models.Uom.name == to_uom_name).first() # type: models.Uom

            if not from_uom or not to_uom:
                logger.error(f"[SYSTEM] Could not find from_uom '{from_uom_name}' and/or to_uom {to_uom_name}.")
                # TODO: Come up with a better error.
                raise Exception(f"Could not find from_uom '{from_uom_name}' and/or to_uom {to_uom_name}.")

            uom_conversion["from_uom_id"] = from_uom.id
            uom_conversion["to_uom_id"] = to_uom.id

            obj = session.query(models.UomConversion).filter_by(from_uom_id=from_uom.id, to_uom_id=to_uom.id).first() # type: models.UomConversion
            if not obj:
                obj = models.UomConversion(**uom_conversion)
                session.add(obj)
                session.commit()
                logger.info(f"[SYSTEM] Created '{obj}'")
            else:
                logger.debug(f"[SYSTEM] UomConversion '{obj}' already exists.")


        



default_user = {
    "first_name": "Admin",
    "last_name": "User",
    "username": "admin",
    "password": "admin"
}


uoms = [
    {
        "code": "ea",
        "description": "A single item.",
        "name": "Each",
        "read_only": True,
        "type_name": "Count"
    },
    {
        "code": "ft",
        "description": "Basic US unit of length.",
        "name": "Foot",
        "read_only": True,
        "type_name": "Length"
    },
    {
        "code": "lbs",
        "description": "Basic US unit of weight.",
        "name": "Pound",
        "read_only": True,
        "type_name": "Weight"
    },
    {
        "code": "hr",
        "description": "Basic unit of time.",
        "name": "Hour",
        "read_only": True,
        "type_name": "Time"
    },
    {
        "code": "gal",
        "description": "Basic US unit of liquid volume.",
        "name": "Gallon",
        "type_name": "Volume"
    },
    {
        "code": "floz",
        "description": "US unit of liquid volume.",
        "name": "Fluid Ounce",
        "type_name": "Volume"
    },
    {
        "code": "in",
        "description": "US unit of length.",
        "name": "Inch",
        "read_only": True,
        "type_name": "Length"
    },
    {
        "code": "in",
        "description": "US unit of length.",
        "name": "Inch",
        "read_only": True,
        "type_name": "Length"
    },
    {
        "code": "kg",
        "description": "Metric unit of weight.",
        "name": "Kilogram",
        "read_only": True,
        "type_name": "Weight"
    },
    {
        "code": "oz",
        "description": "US unit of weight.",
        "name": "Ounce",
        "read_only": True,
        "type_name": "Weight"
    },
    {
        "code": "m",
        "description": "Basic metric unit of length.",
        "name": "Meter",
        "read_only": True,
        "type_name": "Length"
    },
    {
        "code": "L",
        "description": "Basic metric unit of liquid volume.",
        "name": "Liter",
        "read_only": True,
        "type_name": "Volume"
    },
    {
        "code": "amp",
        "description": "Basic unit of electrical current.",
        "name": "Ampere",
        "read_only": True,
        "type_name": "Current"
    },
    {
        "code": "Ω",
        "description": "Basic unit of electrical resistance.",
        "name": "Ohm",
        "read_only": True,
        "type_name": "Resistance"
    },
    {
        "code": "mm",
        "description": "1/1000 of a meter.",
        "name": "Millimeter",
        "type_name": "Length"
    },
    {
        "code": "cm",
        "description": "1/100 of a meter.",
        "name": "Centimeter",
        "type_name": "Length"
    },
    {
        "code": "km",
        "description": "1000 meters.",
        "name": "Kilometer",
        "type_name": "Length"
    },
    {
        "code": "g",
        "description": "Metric unit of weight.",
        "name": "Gram",
        "type_name": "Weight"
    },
    {
        "code": "mg",
        "description": "1/1000 of a gram.",
        "name": "Milligram",
        "type_name": "Weight"
    },
    {
        "code": "mL",
        "description": "1/1000 of a Liter.",
        "name": "Milliliter",
        "type_name": "Volume"
    },
    {
        "code": "min",
        "description": "1/60 of a hour.",
        "name": "Minute",
        "type_name": "Time"
    },
    {
        "code": "yd",
        "description": "Basic US unit of length.",
        "name": "Yard",
        "type_name": "Length"
    },
    {
        "code": "mA",
        "description": "Basic unit of electrical current.",
        "name": "Milliampere",
        "type_name": "Current"
    }
]


uom_conversions = [
    {
        "description": "1 Foot = 12 Inch",
        "from_uom_name": "Foot",
        "to_uom_name": "Inch",
        "factor": 1,
        "multiply": 12
    },
    {
        "description": "12 Inch = 1 Foot",
        "from_uom_name": "Inch",
        "to_uom_name": "Foot",
        "factor": 12,
        "multiply": 1
    },
    {
        "description": "1 Gallon = 128 Fluid Ounce",
        "from_uom_name": "Gallon",
        "to_uom_name": "Fluid Ounce",
        "factor": 1,
        "multiply": 128
    },
    {
        "description": "128 Fluid Ounce = 1 Gallon",
        "from_uom_name": "Fluid Ounce",
        "to_uom_name": "Gallon",
        "factor": 128,
        "multiply": 1
    },
    {
        "description": "2.2046 Pound = 1 Kilogram",
        "from_uom_name": "Pound",
        "to_uom_name": "Kilogram",
        "factor": 2.2046,
        "multiply": 1
    },
    {
        "description": "1 Kilogram = 2.2046 Pound",
        "from_uom_name": "Kilogram",
        "to_uom_name": "Pound",
        "factor": 1,
        "multiply": 2.2046
    },
    {
        "description": "3.2808 Foot = 1 Meter",
        "from_uom_name": "Foot",
        "to_uom_name": "Meter",
        "factor": 3.2808,
        "multiply": 1
    },
    {
        "description": "1 Meter = 3.2808 Foot",
        "from_uom_name": "Meter",
        "to_uom_name": "Foot",
        "factor": 1,
        "multiply": 3.2808
    },
    {
        "description": "3.7854 Liter = 1 Gallon",
        "from_uom_name": "Liter",
        "to_uom_name": "Gallon",
        "factor": 3.7854,
        "multiply": 1
    },
    {
        "description": "1 Gallon = 3.7854 Liter",
        "from_uom_name": "Gallon",
        "to_uom_name": "Liter",
        "factor": 1,
        "multiply": 3.7854
    },
    {
        "description": "1 Meter = 1000 Millimeter",
        "from_uom_name": "Meter",
        "to_uom_name": "Millimeter",
        "factor": 1,
        "multiply": 1000
    },
    {
        "description": "1000 Millimeter = 1 Meter",
        "from_uom_name": "Millimeter",
        "to_uom_name": "Meter",
        "factor": 1000,
        "multiply": 1
    },
    {
        "description": "1 Meter = 100 Centimeter",
        "from_uom_name": "Meter",
        "to_uom_name": "Centimeter",
        "factor": 1,
        "multiply": 100
    },
    {
        "description": "100 Centimeter = 1 Meter",
        "from_uom_name": "Centimeter",
        "to_uom_name": "Meter",
        "factor": 100,
        "multiply": 1
    },
    {
        "description": "1 Kilometer = 1000 Meter",
        "from_uom_name": "Kilometer",
        "to_uom_name": "Meter",
        "factor": 1,
        "multiply": 1000
    },
    {
        "description": "1000 Meter = 1 Kilometer",
        "from_uom_name": "Meter",
        "to_uom_name": "Kilometer",
        "factor": 1000,
        "multiply": 1
    },
    {
        "description": "1 Gram = 1000 Milligram",
        "from_uom_name": "Gram",
        "to_uom_name": "Milligram",
        "factor": 1,
        "multiply": 1000
    },
    {
        "description": "1000 Milligram = 1 Gram",
        "from_uom_name": "Milligram",
        "to_uom_name": "Gram",
        "factor": 1000,
        "multiply": 1
    },
    {
        "description": "1 Kilogram = 1000 Gram",
        "from_uom_name": "Kilogram",
        "to_uom_name": "Gram",
        "factor": 1,
        "multiply": 1000
    },
    {
        "description": "1000 Gram = 1 Kilogram",
        "from_uom_name": "Gram",
        "to_uom_name": "Kilogram",
        "factor": 1000,
        "multiply": 1
    },
    {
        "description": "1 Liter = 1000 Milliliter",
        "from_uom_name": "Liter",
        "to_uom_name": "Milliliter",
        "factor": 1,
        "multiply": 1000
    },
    {
        "description": "1000 Milliliter = 1 Liter",
        "from_uom_name": "Milliliter",
        "to_uom_name": "Liter",
        "factor": 1000,
        "multiply": 1
    },
    {
        "description": "1 Inch = 25.4 Millimeter",
        "from_uom_name": "Inch",
        "to_uom_name": "Millimeter",
        "factor": 1,
        "multiply": 25.4
    },
    {
        "description": "25.4 Millimeter = 1 Inch",
        "from_uom_name": "Millimeter",
        "to_uom_name": "Inch",
        "factor": 25.4,
        "multiply": 1
    },
    {
        "description": "1 Pound = 453.59237 Gram",
        "from_uom_name": "Pound",
        "to_uom_name": "Gram",
        "factor": 1,
        "multiply": 453.59237
    },
    {
        "description": "453.59237 Gram = 1 Pound",
        "from_uom_name": "Gram",
        "to_uom_name": "Pound",
        "factor": 453.59237,
        "multiply": 1
    },
    {
        "description": "1 Pound = 453592.37 Milligram",
        "from_uom_name": "Pound",
        "to_uom_name": "Milligram",
        "factor": 1,
        "multiply": 453592.37
    },
    {
        "description": "453592.37 Milligram = 1 Pound",
        "from_uom_name": "Milligram",
        "to_uom_name": "Pound",
        "factor": 453592.37,
        "multiply": 1
    },
    {
        "description": "1 Pound = 16 Ounce",
        "from_uom_name": "Pound",
        "to_uom_name": "Ounce",
        "factor": 1,
        "multiply": 16
    },
    {
        "description": "16 Ounce = 1 Pound",
        "from_uom_name": "Ounce",
        "to_uom_name": "Pound",
        "factor": 16,
        "multiply": 1
    },
    {
        "description": "91.44 Centimeter = 1 Yard",
        "from_uom_name": "Centimeter",
        "to_uom_name": "Yard",
        "factor": 91.44,
        "multiply": 1
    },
    {
        "description": "1 Yard = 91.44 Centimeter",
        "from_uom_name": "Yard",
        "to_uom_name": "Centimeter",
        "factor": 1,
        "multiply": 91.44
    },
    {
        "description": "0.9144 Meter = 1 Yard",
        "from_uom_name": "Meter",
        "to_uom_name": "Yard",
        "factor": 0.9144,
        "multiply": 1
    },
    {
        "description": "1 Yard = 0.9144 Meter",
        "from_uom_name": "Yard",
        "to_uom_name": "Meter",
        "factor": 1,
        "multiply": 0.9144
    },
    {
        "description": "36 Inch = 1 Yard",
        "from_uom_name": "Inch",
        "to_uom_name": "Yard",
        "factor": 36,
        "multiply": 1
    },
    {
        "description": "1 Yard = 36 Inch",
        "from_uom_name": "Yard",
        "to_uom_name": "Inch",
        "factor": 1,
        "multiply": 36
    },
    {
        "description": "3 Foot = 1 Yard",
        "from_uom_name": "Foot",
        "to_uom_name": "Yard",
        "factor": 3,
        "multiply": 1
    },
    {
        "description": "1 Yard = 3 Foot",
        "from_uom_name": "Yard",
        "to_uom_name": "Foot",
        "factor": 1,
        "multiply": 3
    },
    {
        "description": "914.4 Millimeter = 1 Yard",
        "from_uom_name": "Millimeter",
        "to_uom_name": "Yard",
        "factor": 914.4,
        "multiply": 1
    },
    {
        "description": "1 Yard = 914.4 Millimeter",
        "from_uom_name": "Yard",
        "to_uom_name": "Millimeter",
        "factor": 1,
        "multiply": 914.4
    },
    {
        "description": "1 Hour = 60 Minute",
        "from_uom_name": "Hour",
        "to_uom_name": "Minute",
        "factor": 1,
        "multiply": 60
    },
    {
        "description": "60 Minute = 1 Hour",
        "from_uom_name": "Minute",
        "to_uom_name": "Hour",
        "factor": 60,
        "multiply": 1
    },
    {
        "description": "1 Ampere = 1000 Milliampere",
        "from_uom_name": "Ampere",
        "to_uom_name": "Milliampere",
        "factor": 1,
        "multiply": 1000
    },
    {
        "description": "1 Milliampere = 0.001 Ampere",
        "from_uom_name": "Milliampere",
        "to_uom_name": "Ampere",
        "factor": 1000,
        "multiply": 1
    }
    
]