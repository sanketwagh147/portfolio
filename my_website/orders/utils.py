from datetime import datetime


def generate_order_number(pk):
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    return current_datetime + str(pk)
