
import frappe
from frappe import _

import io
from barcode import (
    EAN13, EAN8, UPCA, Code39, ISBN13, ISBN10, ISSN, JAN, PZN
)
from barcode.writer import ImageWriter

BARCODE_CLASSES = {
    "EAN-13": EAN13,
    "EAN-8": EAN8,
    "EAN-12": UPCA,
    "UPC-A": UPCA,
    "UPC": UPCA,
    "CODE-39": Code39,
    "ISBN-13": ISBN13,
    "ISBN-10": ISBN10,
    "ISBN": ISBN13,
    "ISSN": ISSN,
    "JAN": JAN,
    "PZN": PZN,
    "GS1": Code39,
}


def generate_barcode_image(code: str, barcode_type: str):
    buffer = io.BytesIO()
    barcode_class = BARCODE_CLASSES.get(barcode_type, Code39)
    barcode_class(code, writer=ImageWriter()).write(buffer)
    return buffer.getvalue()


@frappe.whitelist()
def update_item_barcodes(item_name):

    doc = frappe.get_doc("Item", item_name)
    for row in doc.barcodes:
        if row.barcode and row.barcode_type and not row.custom_barcode_attach:
            try:
                img_data = generate_barcode_image(row.barcode, row.barcode_type)

                file_doc = frappe.get_doc({
                    "doctype": "File",
                    "file_name": f"{row.barcode}.png",
                    "is_private": 0,
                    "content": img_data,
                    "attached_to_doctype": "Item",
                    "attached_to_name": doc.name
                }).insert(ignore_permissions=True)

                row.custom_barcode_attach = file_doc.file_url

            except Exception as e:
                frappe.msgprint(
                    f"❌ Barcode generation failed for {row.barcode} "
                    f"({row.barcode_type}): {str(e)}",
                    indicator="red",
                    alert=True
                )

    doc.save(ignore_permissions=True)



@frappe.whitelist()
def set_barcode_attach(doc, method):
    frappe.msgprint('hello')
    for row in doc.items:
        if row.barcode and row.item_code:
            attach = frappe.db.get_value("Item Barcode", {
                "parent": row.item_code,   # parent = Item name
                "barcode": row.barcode
            }, "custom_barcode_attach")

            if attach:
                row.custom_barcode_attach = attach
