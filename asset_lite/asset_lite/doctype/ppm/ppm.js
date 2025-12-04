// Copyright (c) 2024, seyfert and contributors
// For license information, please see license.txt

frappe.ui.form.on('PPM', {
    refresh: function(frm) {
        // Hide the default print icon
        frm.page.hide_icon_group('print');
        
        // Add custom button for PPM Sticker with a print icon
        frm.add_custom_button(
            `<i class="fa fa-print"></i> ${__('PPM Sticker')}`, 
            function() {
                // Set PPM Sticker as the default print format and open print preview
                const customLink = `/printview?doctype=PPM&name=${frm.doc.name}&trigger_print=1&format=PPM%20Sticker&no_letterhead=0`;
                window.open(customLink);
            }
        );
        
        // Add custom button for PPM Service Report with a print icon
        frm.add_custom_button(
            `<i class="fa fa-print"></i> ${__('Service Report')}`, 
            function() {
                // Set Service Report as the default print format and open print preview
                const customLink = `/printview?doctype=PPM&name=${frm.doc.name}&trigger_print=1&format=PPM%20Service%20Report&no_letterhead=0`;
                window.open(customLink);
            }
        );
    }
});



