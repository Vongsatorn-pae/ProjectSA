def convert_to_base_unit(quantity, unit, product_type):
    """แปลงหน่วยสินค้าเป็นหน่วยเล็กที่สุด (g สำหรับ Food และ mL สำหรับ Chemical)"""
    if product_type == 'Food':
        if unit == 'Kg':
            return quantity * 1000  # แปลง Kg เป็น g
        elif unit == 'g':
            return quantity  # ถ้าเป็น g อยู่แล้วไม่ต้องแปลง
        else:
            raise ValueError("Unknown unit for Food")
    
    elif product_type == 'Chemical':
        if unit == 'L':
            return quantity * 1000  # แปลง L เป็น mL
        elif unit == 'mL':
            return quantity  # ถ้าเป็น mL อยู่แล้วไม่ต้องแปลง
        else:
            raise ValueError("Unknown unit for Chemical")
    
    else:
        raise ValueError("Unknown product type")

def convert_to_largest_unit(quantity, product_type):
    """เปลี่ยนหน่วยเป็นหน่วยใหญ่ที่สุด (Kg สำหรับ Food และ L สำหรับ Chemical)"""
    if product_type == 'Food':
        if quantity >= 1000:
            return quantity / 1000, 'Kg'  # แปลงกลับเป็น Kg ถ้าจำนวน >= 1000g
        else:
            return quantity, 'g'  # แสดงเป็น g ถ้าน้อยกว่า 1000g

    elif product_type == 'Chemical':
        if quantity >= 1000:
            return quantity / 1000, 'L'  # แปลงกลับเป็น L ถ้าจำนวน >= 1000mL
        else:
            return quantity, 'mL'  # แสดงเป็น mL ถ้าน้อยกว่า 1000mL

    else:
        raise ValueError("Unknown product type")


def convert_to_base_unit1(quantity, unit, product_type):
    """Convert quantities to a base unit."""
    if product_type == 'Food' and unit == 'Kg':
        return quantity * 1000  # Convert Kg to grams
    elif product_type == 'Chemical' and unit == 'L':
        return quantity * 1000  # Convert liters to milliliters
    return quantity  # No conversion needed for other units
