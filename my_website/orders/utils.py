from datetime import datetime
import simplejson as json


def generate_order_number(pk):
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    return current_datetime + str(pk)


def order_total_by_vendor(order, vendor_id):
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor_id))
    subtotal = tax = 0
    tax_dict = {}

    for key, val in data.items():
        subtotal += float(key)
        val = val.replace("'", '"')
        val = json.loads(val)
        tax_dict |= val
        for i in val:
            for j in val[i]:
                tax += float(val[i][j])

    grand_total = float(subtotal) + float(tax)
    return {"subtotal": subtotal, "tax_dict": tax_dict, "grand_total": grand_total}
