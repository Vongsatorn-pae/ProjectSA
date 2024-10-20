def convert_to_base_unit(quantity, unit, product_type):
    """แปลงหน่วยสินค้าเป็นหน่วยเล็กที่สุด (g สำหรับ Food และ mL สำหรับ Chemical)"""
    if product_type == 'Food':
        if unit == 'kg':
            return quantity * 1000  # แปลง kg เป็น g
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
