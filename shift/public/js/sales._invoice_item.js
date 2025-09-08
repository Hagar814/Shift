frappe.ui.form.on('Sales Invoice Item', {
    barcode: function(frm, cdt, cdn) {
        console.log("Barcode changed in child row");  // debug log
        let row = locals[cdt][cdn];
        
        if (row.barcode && row.item_code) {
            frappe.call({
                method: "your_app.api.get_barcode_attach",
                args: {
                    barcode: row.barcode,
                    item_code: row.item_code
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "custom_barcode_attach", r.message || "");
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, "custom_barcode_attach", "");
        }
    }
});

