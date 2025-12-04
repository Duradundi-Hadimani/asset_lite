frappe.pages['asset-history'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Asset History',
        single_column: false // Allows multi-column layout
    });


    // Add custom styles
    $('head').append(`
        <style>
            .section-header {
                background-color: #007bff;
                // background-color: #4ce1f5;
                color: white;
                padding: 10px;
                border-radius: 5px;
                margin-top: 20px;
            }
            .section-header_wo {
                background-color:rgb(246, 226, 168);
                color: black;
                padding: 10px;
                border-radius: 5px;
                margin-top: 20px;
            }
            .table th {
                background-color: #f8f9fa;
            }
            .badge-status {
                font-size: 14px;
                padding: 5px 10px;
                border-radius: 10px;
            }
            .badge-completed {
                background-color: #28a745;
                color: white;
            }
            .badge-pending {
                background-color: #ffc107;
                color: black;
            }
            .badge-planned {
                background-color: #17a2b8;
                color: white;
            }
        </style>
    `);

    // Create a container for layout
    $(wrapper).append(`
        <div class="row">
            <div class="col-md-3" id="filter_section"></div>
            <div class="col-md-9">
                <div id="content_section"></div>
                <div id="work_orders_section"></div>
				<div id="spare_parts_section"></div>
                <div id="maintenance_section"></div>
            </div>
        </div>
    `);

    // Create Asset Filter
    let asset_filter = new frappe.ui.form.ControlLink({
        parent: $("#filter_section"),
        df: {
            label: "Select Asset",
            fieldname: "asset",
            options: "Asset",
            change: function() {
                let asset_id = asset_filter.get_value();
                if (asset_id) {
                    fetch_asset_details(asset_id);
                }
            }
        }
    });

    asset_filter.make_input(); // Render the filter field

    // **Fix: Wait until the input is ready before setting the value**
    let params = new URLSearchParams(window.location.search);
    let asset_id = params.get("asset"); // Get asset from URL

    if (asset_id) {
        setTimeout(() => {
            asset_filter.set_value(asset_id); // Apply the value after render
            fetch_asset_details(asset_id); // Fetch data immediately
        }, 500); // Delay to ensure input is initialized
    }

    // Function to Fetch Asset Details
    function fetch_asset_details(asset_id) {
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Asset",
                name: asset_id
            },
            callback: function(response) {
                if (response.message) {
                    let asset = response.message;
                    
                    $("#content_section").html(`
                        <h3 class="section-header">🔍 Asset Details</h3>
                        <p><strong>ID:</strong> <a href="/app/asset/${asset.name}" class="badge bg-info text-white">${asset.name}</a></p>
                        <p><strong>Name:</strong> ${asset.asset_name}</p>
                        <p><strong>🏥 Hospital:</strong> ${asset.company}</p>
                        <p><strong>📍 Location:</strong> ${asset.location}</p>
                        <p><strong>🚛 Supplier:</strong> ${asset.supplier}</p>
                        <p><strong>💰 Total Repair Cost:</strong> <span class="badge bg-warning text-dark">${asset.custom_total_spare_parts_amount}</span></p>
                    `);

                    $("#work_orders_section").html(`<h3 class="section-header">🔗 Linked Work Orders</h3><div id="work_orders_table"></div>`);
                    $("#spare_parts_section").html(`<h3 class="section-header">🛠️ Items Used for Repair</h3><div id="spare_parts_table"></div>`);

                    // Fetch Work Orders After Asset Details Are Shown
                    fetch_work_orders(asset_id);
					fetch_spare_parts(asset_id);
                    fetch_maintenance_details(asset_id);
                }
            }
        });
    }

    // Function to Fetch and Display Linked Work Orders
    function fetch_work_orders(asset_id) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Work_Order",
                filters: { asset: asset_id },
                fields: ["name", "work_order_type","repair_status","creation","total_repair_cost"]
            },
            callback: function(response) {
                if (response.message) {
                    let work_orders = response.message;
                    
                    // If no work orders found
                    if (work_orders.length === 0) {
                        $("#work_orders_table").html("<p>No Work Orders Found for this Asset.</p>");
                        return;
                    }

                    // Create a formatted table for Work Orders
                    let html = `
                        <div class="table-responsive">
                            <table class="table table-striped table-hover table-bordered">
                                <thead class="table-primary">
                                    <tr>
                                        <th>Work Order No</th>
                                        <th>Work Order Type</th>
                                        <th>Repair Status</th>
                                        <th>Repair Cost</th>
                                        <th>Created On</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;

                    // Append Work Order details in table rows
                    work_orders.forEach(wo => {
                        // Determine status badge color
                        let status_class = "";
                        if (wo.repair_status === "Completed") {
                            status_class = "badge-success"; // Green
                        } else if (wo.repair_status === "Work In Progress") {
                            status_class = "badge-warning"; // Yellow
                        } else {
                            status_class = "badge-secondary"; // Gray (default)
                        }


                        html += `
                            <tr>
                                <td><a href="/app/work_order/${wo.name}" class="fw-bold text-primary">${wo.name}</a></td>
								<td>${wo.work_order_type}</td>
								<td><span class="badge ${status_class}">${wo.repair_status}</span></td>
								<td><strong>${parseFloat(wo.total_repair_cost).toFixed(2)}ر.س</strong></td>
                                <td>${wo.creation}</td>
                            </tr>
                        `;
                    });

                    html += `
                                </tbody>
                            </table>
                        </div>
                    `;

                    // Insert into the work_orders_section
                    $("#work_orders_table").html(html);
                }
            }
        });
    }

	// Function to Fetch and Display Spare Parts
    function fetch_spare_parts(asset_id) {
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Asset",
                name: asset_id
            },
            callback: function(response) {
                if (response.message && response.message.custom_spare_parts) {
                    let spare_parts = response.message.custom_spare_parts;
                    
                    if (spare_parts.length === 0) {
                        $("#spare_parts_table").html("<p>No Spare Parts Used for this Asset.</p>");
                        return;
                    }

                    // Group spare parts by work_order
                    let grouped_parts = {};
                    spare_parts.forEach(sp => {
                        if (!grouped_parts[sp.work_order]) {
                            grouped_parts[sp.work_order] = [];
                        }
                        grouped_parts[sp.work_order].push(sp);
                    });

                    // Create HTML for Spare Parts Table
                    let html = `<div class="table-responsive">`;

                    Object.keys(grouped_parts).forEach(work_order => {
                        html += `
                            <h4 class="section-header_wo">Work Order: <a href="/app/work_order/${work_order}">${work_order ? work_order : ""}</a></h4>
                            <table class="table table-striped table-hover table-bordered">
                                <thead class="table-primary">
                                    <tr>
                                        <th>Item Name</th>
                                        <th>Quantity</th>
										<th>Cost</th>
                                        <th>Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                        `;

                        grouped_parts[work_order].forEach(sp => {
                            html += `
                                <tr>
                                    <td>${sp.item_code}</td>
                                    <td>${sp.qty}</td>
									<td>${sp.rate}ر.س</td>
									<td>${sp.amount}ر.س</td>
                                </tr>
                            `;
                        });

                        html += `
                                </tbody>
                            </table>
                        `;
                    });

                    html += `</div>`;

                    // Insert into the spare_parts_section
                    $("#spare_parts_table").html(html);
                }
            }
        });
    }

    // Fetch Asset Maintenance Details (Including Tasks)
function fetch_maintenance_details(asset_id) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Asset Maintenance",
            filters: { asset_name: asset_id },
            fields: ["name", "maintenance_team", "custom_type_of_maintenance"],
            limit_page_length: 10
        },
        callback: function(response) {
            if (response.message) {
                let maintenance_records = response.message;
                if (maintenance_records.length === 0) {
                    $("#maintenance_section").html("<p>No Maintenance Records Found.</p>");
                    return;
                }

                let html = `<h3 class="section-header">🛠️ Asset Maintenance Details</h3>`;

                maintenance_records.forEach(m => {
                    html += `
                        <div class="maintenance-card">
                            <p><strong>Maintenance ID:</strong> <a href="/app/asset-maintenance/${m.name}">${m.name}</a></p>
                            <p><strong>Maintenance Team:</strong> ${m.maintenance_team}</p>
                            <p><strong>Type of Maintenance:</strong> ${m.custom_type_of_maintenance}</p>
                        </div>
                    `;

                    // Fetch Maintenance Tasks (Child Table) for Each Record
                    fetch_maintenance_tasks(m.name);
                });

                $("#maintenance_section").html(html);
            }
        }
    });
}

function fetch_maintenance_tasks(maintenance_id) {
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Asset Maintenance",
            name: maintenance_id
        },
        callback: function(response) {
            if (response.message && response.message.asset_maintenance_tasks) {
                let tasks = response.message.asset_maintenance_tasks;
                if (tasks.length === 0) {
                    $("#maintenance_section").append("<p>No Maintenance Tasks Found.</p>");
                    return;
                }

                // Clear the section to avoid duplicate entries
                $("#maintenance_section").find(".maintenance-tasks").remove();

                let html = `
                    <div class="maintenance-tasks">
                        <h4 class="section-header"><br>Maintenance Tasks for <a href="/app/asset-maintenance/${maintenance_id}">${maintenance_id}</a></h4>
                        <div class="table-responsive">
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Assigned To</th>
                                        <th>Periodicity</th>
                                        <th>Next Due Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                `;

                tasks.forEach(task => {
                    html += `
                        <tr>
                            <td>${task.assign_to_name}</td>
                            <td>${task.periodicity}</td>
                            <td>${task.next_due_date}</td>
                        </tr>
                    `;
                });

                html += `</tbody></table></div></div>`;

                $("#maintenance_section").append(html);
                fetch_maintenance_logs(maintenance_id);
            }
        }
    });
}

function fetch_maintenance_logs(maintenance_id) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Asset Maintenance Log",
            filters: { asset_maintenance: maintenance_id },
            fields: ["maintenance_status"]
        },
        callback: function(response) {
            if (response.message) {
                let logs = response.message;
                if (logs.length === 0) {
                    $("#maintenance_section").append("<p>No Maintenance Logs Found.</p>");
                    return;
                }

                // Remove previous log summary
                $("#maintenance_section").find(".maintenance-log-summary").remove();

                let status_counts = {};
                logs.forEach(log => {
                    if (!status_counts[log.maintenance_status]) {
                        status_counts[log.maintenance_status] = 0;
                    }
                    status_counts[log.maintenance_status]++;
                });

                let html = `
                    <div class="maintenance-log-summary">
                        <h4 class="section-header">📜Periodic Maintenance</h4>
                        <div class="table-responsive">
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Maintenance Status</th>
                                        <th>Count</th>
                                    </tr>
                                </thead>
                                <tbody>
                `;

                for (let status in status_counts) {
                    html += `
                        <tr>
                            <td>${status}</td>
                            <td>${status_counts[status]}</td>
                        </tr>
                    `;
                }

                html += `</tbody></table></div></div>`;

                $("#maintenance_section").append(html);
                fetch_detailed_maintenance_logs(maintenance_id);
            }
        }
    });
}

function fetch_detailed_maintenance_logs(maintenance_id) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Asset Maintenance Log",
            filters: { asset_maintenance: maintenance_id },
            fields: [
                "name",
                "maintenance_status",
                "assign_to_name",
                "maintenance_type",
                "due_date",
                "completion_date",
                "periodicity",
                "actions_performed"
            ],
            order_by: "completion_date desc"
        },
        callback: function(response) {
            if (response.message) {
                let logs = response.message;
                if (logs.length === 0) {
                    $("#maintenance_section").append("<p>No Maintenance Logs Found.</p>");
                    return;
                }

                // Remove previous detailed logs
                $("#maintenance_section").find(".maintenance-logs").remove();

                let completed_logs = logs.filter(log => log.maintenance_status === "Completed");
                let remaining_logs = logs.filter(log => log.maintenance_status !== "Completed");

                let html = `<div class="maintenance-logs">`;

                // ✅ Display Completed Logs First
                if (completed_logs.length > 0) {
                    html += `
                        <h4 class="section-header">✅ Completed Maintenance Logs</h4>
                        <div class="table-responsive">
                            <table class="table table-striped table-hover table-bordered">
                                <thead class="table-primary">
                                    <tr>
                                        <th>Log ID</th>
                                        <th>Assigned To</th>
                                        <th>Maintenance Type</th>
                                        <th>Due Date</th>
                                        <th>Completion Date</th>
                                        <th>Periodicity</th>
                                        <th>Actions Performed</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;

                    completed_logs.forEach(log => {
                        html += `
                            <tr>
                                <td><a href="/app/asset-maintenance-log/${log.name}">${log.name}</a></td>
                                <td>${log.assign_to_name}</td>
                                <td>${log.maintenance_type}</td>
                                <td>${log.due_date}</td>
                                <td>${log.completion_date}</td>
                                <td>${log.periodicity}</td>
                                <td>${log.actions_performed ? log.actions_performed : ""}</td>
                            </tr>
                        `;
                    });

                    html += `</tbody></table></div>`;
                }

                // ✅ Display Remaining Logs
                if (remaining_logs.length > 0) {
                    html += `
                        <h4 class="section-header">⏳ Pending/Planned Maintenance Logs</h4>
                        <div class="table-responsive">
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Log ID</th>
                                        <th>Assigned To</th>
                                        <th>Maintenance Type</th>
                                        <th>Due Date</th>
                                        <th>Periodicity</th>
                                        <th>Maintenance Status</th>
                                        <th>Actions Performed</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;

                    remaining_logs.forEach(log => {
                        html += `
                            <tr>
                                <td><a href="/app/asset-maintenance-log/${log.name}">${log.name}</a></td>
                                <td>${log.assign_to_name}</td>
                                <td>${log.maintenance_type}</td>
                                <td>${log.due_date}</td>
                                <td>${log.periodicity}</td>
                                <td><strong>${log.maintenance_status}</strong></td>
                                <td>${log.actions_performed ? log.actions_performed : ""}</td>
                            </tr>
                        `;
                    });

                    html += `</tbody></table></div>`;
                }

                html += `</div>`; // Close maintenance logs section

                $("#maintenance_section").append(html);
            }
        }
    });
}



};
