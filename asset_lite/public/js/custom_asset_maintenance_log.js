
frappe.ui.form.on('Asset Maintenance Log', {
    refresh: function(frm) {
        // Hide the default print icon
        frm.page.hide_icon_group('print');
        
        // Add custom button for PPM Sticker with a print icon
        frm.add_custom_button(
            `<i class="fa fa-print"></i> ${__('PPM Sticker')}`, 
            
            function() {
               
                // Set PPM Sticker as the default print format and open print preview
                const customLink = `/printview?doctype=Asset Maintenance Log&name=${frm.doc.name}&trigger_print=0&format=PPM%20Asset&no_letterhead=0`;
                window.open(customLink);
            }
        );
        
        // Add custom button for PPM Service Report with a print icon
        frm.add_custom_button(
            `<i class="fa fa-print"></i> ${__('Service Report')}`, 
            function() {
                // Set Service Report as the default print format and open print preview
                const customLink = `/printview?doctype=Asset Maintenance Log&name=${frm.doc.name}&trigger_print=0&format=PPM%20Asset%20Service&no_letterhead=0`;
                window.open(customLink);
            }
        );
    }
});