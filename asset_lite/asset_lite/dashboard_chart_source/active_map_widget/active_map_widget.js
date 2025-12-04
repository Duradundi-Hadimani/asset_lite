frappe.dashboards.chart_sources["Active Map Widget"] = {
    method: "asset_lite.map.get_custom_html_data",
    filters: []
};

// Override the chart rendering after data is loaded
frappe.provide('frappe.dashboards');

$(document).on('app_ready', function() {
    // Override the render method for custom HTML charts
    const original_render = frappe.ui.Dashboard.prototype.render_chart;
    
    frappe.ui.Dashboard.prototype.render_chart = function(chart_data, chart_container) {
        if (chart_data.custom_html) {
            // Clear the container and add custom HTML
            chart_container.empty();
            const custom_html = `
                <div style="padding: 20px; background: #f8f9fa; border-radius: 8px; margin: 10px;">
                    <h4 style="margin-bottom: 15px; color: #333;">Custom Dashboard Content</h4>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card" style="border: 1px solid #ddd; padding: 15px;">
                                <h5>Card Title 1</h5>
                                <p>Your custom content here</p>
                                <button class="btn btn-primary btn-sm">Action Button</button>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card" style="border: 1px solid #ddd; padding: 15px;">
                                <h5>Card Title 2</h5>
                                <p>More custom content</p>
                                <div class="progress" style="height: 20px;">
                                    <div class="progress-bar" style="width: 75%">75%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            chart_container.html(custom_html);
            return;
        }
        // Call original render method for other charts
        return original_render.call(this, chart_data, chart_container);
    };
});

