// Copyright (c) 2024, seyfert and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Work_Order", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Work_Order", {
    refresh(frm) {
        // Call the server-side method to get the site version type
        frm.call({
            method: "check_site_version",
            doc: frm.doc,
            callback: function(response) {
                // The returned site version type
                var site_version = response.message;

                if (site_version === "lite") {
                    frm.set_df_property("need_spare_parts_purchase", "hidden", 1);
                    // frappe.msgprint("The Need Procurement checkbox is hided as the site version is 'lite'.");
                } else {
                    frm.set_df_property("need_spare_parts_purchase", "hidden", 0);
                }
            }
        });
       
            // Hide the default print icon
            frm.page.hide_icon_group('print');
            
            
            // Add custom button for PPM Service Report with a print icon
            /*frm.add_custom_button(
                `<i class="fa fa-print"></i> ${__('Service Report')}`, 
                function() {
                    // Set Service Report as the default print format and open print preview
                    const customLink = `/printview?doctype=Work_Order&name=${frm.doc.name}&trigger_print=0&format=Service%20Report&no_letterhead=0`;
                    window.open(customLink);
                }
            );*/
            if(frm.doc.company=='King Fahad Hospital'){
            frm.add_custom_button(
                `<i class="fa fa-print"></i> ${__('SR-King Fahad Hospital')}`, 
                function() {
                    // Set Service Report as the default print format and open print preview
                    const customLink = `/printview?doctype=Work_Order&name=${frm.doc.name}&trigger_print=0&format=Service%20Report&no_letterhead=0`;
                    window.open(customLink);
                }
            );
        }
        if(frm.doc.company=='King Khalid Hospital'){
            frm.add_custom_button(
                `<i class="fa fa-print"></i> ${__('SR-King Khalid Hospital')}`, 
                function() {
                    // Set Service Report as the default print format and open print preview
                    const customLink = `/printview?doctype=Work_Order&name=${frm.doc.name}&trigger_print=0&format=Service%20Report(KK)&no_letterhead=0`;
                    window.open(customLink);
                }
            );
        }
        
    },
    /*setup: (frm) => {
        frm.set_query("assign_to", "asset_maintenance_tasks", function (doc) {
			return {
				query: "erpnext.assets.doctype.asset_maintenance.asset_maintenance.get_team_members",
				filters: {
					maintenance_team: doc.maintenance_team,
				},
			};
		});
    
    }*/
});
