frappe.pages['active-map'].on_page_load = function(wrapper) {
        var page = frappe.ui.make_app_page({
                parent: wrapper,
                title: 'Active Map',
                single_column: true
        });
	
	// Load Leaflet CSS
	$('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />').appendTo('head');
	
	// Load Leaflet JS
	$.getScript('https://unpkg.com/leaflet@1.7.1/dist/leaflet.js', function() {
		// Initialize the map after Leaflet is loaded
		new AssetMap(page, wrapper);
	});
};

class AssetMap {
	constructor(page, wrapper) {
		this.page = page;
		this.wrapper = wrapper;
		this.setup_page();
	}
	
	setup_page() {
		// Add filters
		this.setup_filters();
		
		// Create map container
		this.make_map_container();
		
		// Add custom styles
		this.add_custom_styles();
		
		// Initialize map
		this.initialize_map();
	}
	
	setup_filters() {
		let filter_container = $('<div class="filter-container"></div>').prependTo(this.page.main);
    
		// Add a filter for hospital/company
		this.page.add_field({
			parent: filter_container,
			fieldname: 'company',
			label: __('Hospital'),
			fieldtype: 'Link',
			options: 'Location', // Using Location DocType for hospitals
			get_query: () => {
				return {
					filters: {
						custom_is_hospital: 1
					}
				};
			},
			onchange: () => this.fetch_and_render_data()
		});
	}
	
	make_map_container() {
		this.$map_container = $('<div id="asset_map" style="height: 600px; width: 100%;"></div>')
			.appendTo(this.page.main);
	}
	
	add_custom_styles() {
		// Add custom CSS for tooltips and popups
		if (!$('#asset-map-styles').length) {
			$('<style id="asset-map-styles">')
				.prop("type", "text/css")
				.html(`
					.hospital-tooltip {
						background-color: white;
						border: 1px solid #ccc;
						border-radius: 5px;
						padding: 8px;
						font-size: 12px;
						box-shadow: 0 2px 5px rgba(0,0,0,0.2);
					}
					
					.hospital-popup {
						font-size: 12px;
						min-width: 260px;   /* ensures a minimum width */
						max-width: 260px;   /* keeps all the same width */
						white-space: normal; /* allows wrapping of long text */
						word-wrap: break-word; /* breaks long words if needed */
					}
					.hospital-popup .hospital-name {
						font-weight: bold;
						font-size: 14px;
						margin-bottom: 4px;
					}
					.hospital-popup .asset-count {
						margin-bottom: 3px;
					}
					.hospital-popup .view-assets {
						margin-top: 10px;
					}
					/* ✅ Ensure Filter Dropdown Stays Above the Map */
                .frappe-control {
                    position: relative;
                    z-index: 1000;
                }
                .select2-container {
                    z-index: 1050 !important;
                }
				.filter-container {
					position: relative;
					padding-bottom: 10px;
					background: white;
					z-index: 1000;
				}
				/* ✅ Red Flashing Animation for Urgent Work Orders */
				.urgent-marker {
					animation: urgent-flash 2s infinite;
				}
				
				@keyframes urgent-flash {
					0%, 50% {
						filter: hue-rotate(0deg) brightness(1) saturate(1);
					}
					25%, 75% {
						filter: hue-rotate(0deg) brightness(1.5) saturate(2) drop-shadow(0 0 10px red);
					}
				}
				
				/* Red marker style */
				.red-marker {
					filter: hue-rotate(120deg) saturate(2) brightness(0.8);
				}

				/* ✅ Ensure Leaflet popups/cards are always on top */
				.leaflet-popup {
					z-index: 2000 !important;
				}

				.leaflet-tooltip {
					z-index: 2000 !important;
				}

				.leaflet-popup-content-wrapper,
				.leaflet-popup-tip {
					pointer-events: auto !important;
				}

				/* ✅ Hospital Popup Container */
				.hospital-popup-container .leaflet-popup-content-wrapper {
    max-height: 320px;   /* reduce height */
    overflow-y: auto;
    border-radius: 8px;
    padding: 3px 8px;   /* less padding for compact look */
    font-size: 12px;     /* smaller font size */
    line-height: 1.3;    /* tighter spacing */
}

				/* ✅ Responsive popup positioning */
				.leaflet-popup {
					margin-bottom: 20px !important;
				}

				/* ✅ WO Status Table Styles */
				.wo-status-table {
					width: 100%;
					border-collapse: collapse;
					margin: 10px 0;
					font-size: 12px;
				}
				.wo-status-table th,
				.wo-status-table td {
					padding: 4px 8px;
					text-align: left;
					border: 1px solid #ddd;
				}
				.wo-status-table th {
					background-color: #f5f5f5;
					font-weight: bold;
				}
				.status-open {
					background-color: #f8d7da;
                                        color: #721c24;
				}
				.status-progress {
					background-color: #fff3cd;
                                        color: #856404;
				}
				.status-review {
					background-color: #d1ecf1;
					color: #0c5460;
				}
				.status-completed {
					background-color: #d4edda;
                                        color: #155724;
				}
				.wo-status-link {
					cursor: pointer;
					text-decoration: underline;
					font-weight: bold;
				}
				/* ✅ Reduce button size inside popup */
.hospital-popup .btn {
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
}

	
				`)
				.appendTo("head");
		}
	}

/*
	initialize_map() {
    // Initialize map centered in Saudi Arabia with zoom controls and limits
    this.map = L.map('asset_map', {
        zoomControl: true,
        minZoom: 5,
        maxZoom: 10,
        zoomSnap: 0.25  // Enable fractional zoom for smooth zooming
    }).setView([24.8, 45.5], 6);  // Initial center and zoom

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(this.map);

    // Load GeoJSON from external file for Saudi Arabia regions
    fetch("https://raw.githubusercontent.com/wjdanalharthi/GeoJSON-of-Saudi-Arabia-Regions/master/data/SA_regions.json")
    .then(response => response.json())
    .then(saudiGeoJSON => {
        // Add Saudi Arabia regions polygon layer
        const saudiLayer = L.geoJSON(saudiGeoJSON, {
            style: { color: '#ffcc00', weight: 2, fillColor: '#ffe699', fillOpacity: 0.3 }
        }).addTo(this.map);

        // Create world polygon for the mask outside Saudi Arabia
        const world = {
            "type": "Polygon",
            "coordinates": [[
                [-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]
            ]]
        };

        // Extract all Saudi Arabia coordinates from all features and flatten into one array
        let saudiCoordinates = [];
        saudiGeoJSON.features.forEach(feature => {
            if (feature.geometry.type === 'Polygon') {
                saudiCoordinates = saudiCoordinates.concat(feature.geometry.coordinates);
            } else if (feature.geometry.type === 'MultiPolygon') {
                feature.geometry.coordinates.forEach(polygon => {
                    saudiCoordinates = saudiCoordinates.concat(polygon);
                });
            }
        });

        // Create mask polygon with world boundary minus Saudi Arabia polygons (in reverse for holes)
        L.geoJSON({
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        world.coordinates[0],
                        ...saudiCoordinates.map(poly => poly.slice().reverse())
                    ]
                }
            }]
        }, {
            style: { fillColor: '#000000', fillOpacity: 0.85, color: 'none' }
        }).addTo(this.map);

        // Fit map bounds to the Saudi Arabia polygons
        //this.map.fitBounds(saudiLayer.getBounds());

        // Optional: Zoom out slightly if needed to show more surrounding context
        //let currentZoom = this.map.getZoom();
        //if(currentZoom > 5) {
          //  this.map.setZoom(currentZoom - 1);
       // }
    });

    // Fetch and render your hospital/location data after map init
    // Call here only if it doesn't depend on loaded GeoJSON strictly
    this.fetch_and_render_data();
}
*/

	initialize_map() {
		// Initialize the map with a default view
		this.map = L.map('asset_map').setView([20, 0], 2);
		
		// Add OpenStreetMap tile layer
		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(this.map);
		
		// Fetch and plot hospital data
		this.fetch_and_render_data();
	}

	fetch_and_render_data() {
		let filters = {
			latitude: ['!=', ''],
			longitude: ['!=', '']
		};
	
		if (this.page.fields_dict.company && this.page.fields_dict.company.get_value()) {
			filters.name = this.page.fields_dict.company.get_value();
		}
	
		frappe.call({
			method: 'frappe.client.get_list',
			args: {
				doctype: 'Location', // Your DocType for hospital locations
				fields: ['name', 'latitude', 'longitude'],
				filters: filters
			},
			callback: (r) => {
				if (r.message) {
					const locations = r.message;
	
					// For each location, fetch asset, work order, and maintenance log counts
					const promises = locations.map(location => {
						return new Promise((resolve) => {
							let counts = {
								assets: 0,
								normal_work_orders: 0,
								urgent_work_orders: 0,
								planned_maintenance: 0,
								completed_maintenance: 0,
								// New WO status counts
								wo_open: 0,
								wo_progress: 0,
								wo_review: 0,
								wo_completed: 0
							};
	
							// Fetch Asset count
							frappe.call({
								method: 'frappe.client.get_count',
								args: {
									doctype: 'Asset',
									filters: { 'company': location.name }
								},
								callback: (res) => {
									counts.assets = res.message || 0;
	
									// Fetch Normal Work Order count
									frappe.call({
										method: 'frappe.client.get_count',
										args: {
											doctype: 'Work_Order',
											filters: {
												'company': location.name,
												'custom_priority_': 'Normal',
												'repair_status': ['in', ['Open', 'Work In Progress']]
											}
										},
										callback: (res) => {
											counts.normal_work_orders = res.message || 0;
	
											// Fetch Urgent Work Order count
											frappe.call({
												method: 'frappe.client.get_count',
												args: {
													doctype: 'Work_Order',
													filters: {
														'company': location.name,
														'custom_priority_': 'Urgent',
														'repair_status': ['in', ['Open', 'Work In Progress']]
													}
												}
											}).then((res) => {
												counts.urgent_work_orders = res.message || 0;
	
												// Fetch WO Status counts
												const woStatusPromises = [
													// Open
													frappe.call({
														method: 'frappe.client.get_count',
														args: {
															doctype: 'Work_Order',
															filters: {
																'company': location.name,
																'repair_status': 'Open'
															}
														}
													}),
													// Work In Progress
													frappe.call({
														method: 'frappe.client.get_count',
														args: {
															doctype: 'Work_Order',
															filters: {
																'company': location.name,
																'repair_status': 'Work In Progress'
															}
														}
													}),
													// Pending Review
													frappe.call({
														method: 'frappe.client.get_count',
														args: {
															doctype: 'Work_Order',
															filters: {
																'company': location.name,
																'repair_status': 'Pending Review'
															}
														}
													}),
													// Completed
													frappe.call({
														method: 'frappe.client.get_count',
														args: {
															doctype: 'Work_Order',
															filters: {
																'company': location.name,
																'repair_status': 'Completed'
															}
														}
													}),
													// Planned Maintenance
													frappe.call({
														method: 'frappe.client.get_count',
														args: {
															doctype: 'Asset Maintenance Log',
															filters: {
																'custom_hospital_name': location.name,
																'maintenance_status': 'Planned'
															}
														}
													}),
													// Completed Maintenance
													frappe.call({
														method: 'frappe.client.get_count',
														args: {
															doctype: 'Asset Maintenance Log',
															filters: {
																'custom_hospital_name': location.name,
																'maintenance_status': 'Completed'
															}
														}
													}),
													//Overdue Maintenance
                                                                                                        frappe.call({
                                                                                                                method: 'frappe.client.get_count',
                                                                                                                args: {
                                                                                                                        doctype: 'Asset Maintenance Log',
                                                                                                                        filters: {
                                                                                                                                'custom_hospital_name': location.name,
                                                                                                                                'maintenance_status': 'Overdue'
                                                                                                                        }
                                                                                                                }
                                                                                                        })
												];

												Promise.all(woStatusPromises).then(results => {
													counts.wo_open = results[0].message || 0;
													counts.wo_progress = results[1].message || 0;
													counts.wo_review = results[2].message || 0;
													counts.wo_completed = results[3].message || 0;
													counts.planned_maintenance = results[4].message || 0;
													counts.completed_maintenance = results[5].message || 0;
													counts.overdue_maintenance = results[6].message || 0;

													// Resolve after all counts are fetched
													resolve({ ...location, ...counts });
												});
											});
										}
									});
								}
							});
						});
					});
	
					Promise.all(promises).then(results => {
						this.render_map(results);
					});
				}
			}
		});
	}
	
	
	
	render_map(locations) {
		const userLang = frappe.boot.user.language || 'en';
		const isRTL = document.dir === 'rtl' || userLang === 'ar';
		console.log(isRTL)

		if (this.markers_layer) {
			this.map.removeLayer(this.markers_layer);
		}
	
		this.markers_layer = L.layerGroup().addTo(this.map);
		let bounds = L.latLngBounds();
	
		locations.forEach(location => {
			if (!location.latitude || !location.longitude) return;
	
			const lat = parseFloat(location.latitude);
			const lng = parseFloat(location.longitude);
	
			if (isNaN(lat) || isNaN(lng)) return;

			// Create marker with conditional styling based on urgent work orders
	
			const marker = L.marker([lat, lng]).addTo(this.markers_layer);

			// ✅ Apply red flashing effect if there are urgent work orders
			if (location.urgent_work_orders > 0) {
				// Get the marker icon element and add urgent classes
				setTimeout(() => {
					const markerElement = marker.getElement();
					if (markerElement) {
						markerElement.classList.add('urgent-marker', 'red-marker');
					}
				}, 100);
			}
	
			// Create popup content with WO Status Table
			const popupContent = `
				<div class="hospital-popup">
					<div class="hospital-name">${location.name}</div>
					<div class="asset-count">Total Assets: ${location.assets}</div>
					
					<!-- WO Status Table -->
					<div style="margin: 10px 0;">
						<b>Work Order Status:</b>
						<a href="javascript:void(0);"
                                                        style="color: blue; font-weight: bold; text-decoration: none; cursor: pointer;"
                                                        onclick="frappe.set_route('List', 'Work_Order', {
                                                                'company': '${location.name}',
                                                                'custom_priority_': 'Normal',
                                                                'repair_status': ['in', ['Open', 'Work In Progress']]
                                                        })">
                                                         Normal: ${location.normal_work_orders} ,
                                                </a>
						<a href="javascript:void(0);"
                                                        style="color: red; font-weight: bold; text-decoration: none; cursor: pointer;"
                                                        onclick="frappe.set_route('List', 'Work_Order', {
                                                                'company': '${location.name}',
                                                                'custom_priority_': 'Urgent',
                                                                'repair_status': ['in', ['Open', 'Work In Progress']]
                                                        })">
                                                         Urgent : ${location.urgent_work_orders}
                                                </a>
						<table class="wo-status-table">
							<thead>
								<tr>
									<th>Status</th>
									<th>Count</th>
								</tr>
							</thead>
							<tbody>
								<tr class="status-open">
									<td>Open</td>
									<td>
										<span class="wo-status-link" 
											onclick="frappe.set_route('List', 'Work_Order', {
												'company': '${location.name}',
												'repair_status': 'Open'
											})">
											${location.wo_open}
										</span>
									</td>
								</tr>
								<tr class="status-progress">
									<td>Work In Progress</td>
									<td>
										<span class="wo-status-link" 
											onclick="frappe.set_route('List', 'Work_Order', {
												'company': '${location.name}',
												'repair_status': 'Work In Progress'
											})">
											${location.wo_progress}
										</span>
									</td>
								</tr>
								<tr class="status-review">
									<td>Pending Review</td>
									<td>
										<span class="wo-status-link" 
											onclick="frappe.set_route('List', 'Work_Order', {
												'company': '${location.name}',
												'repair_status': 'Pending Review'
											})">
											${location.wo_review}
										</span>
									</td>
								</tr>
								<tr class="status-completed">
									<td>Completed</td>
									<td>
										<span class="wo-status-link" 
											onclick="frappe.set_route('List', 'Work_Order', {
												'company': '${location.name}',
												'repair_status': 'Completed'
											})">
											${location.wo_completed}
										</span>
									</td>
								</tr>
							</tbody>
						</table>
					</div>

					<!--<div class="work-order-count">
						<b>Work Orders by Priority:</b><br>
						<a href="javascript:void(0);" 
							style="color: black; font-weight: bold; text-decoration: none; cursor: pointer;"
							onclick="frappe.set_route('List', 'Work_Order', {
								'company': '${location.name}',
								'custom_priority_': 'Normal',
								'repair_status': ['in', ['Open', 'Work In Progress']]
							})">
							 Normal: ${location.normal_work_orders}
						</a>

    				<br>
					<a href="javascript:void(0);" 
							style="color: red; font-weight: bold; text-decoration: none; cursor: pointer;"
							onclick="frappe.set_route('List', 'Work_Order', {
								'company': '${location.name}',
								'custom_priority_': 'Urgent',
								'repair_status': ['in', ['Open', 'Work In Progress']]
							})">
							 Urgent : ${location.urgent_work_orders}
						</a>
					
				
					</div> -->
					<div class="pm-count">
						<b>Preventive Maintenance:</b><br>
						<a href="javascript:void(0);" 
							style="color: orange; font-weight: bold; text-decoration: none; cursor: pointer;"
							onclick="frappe.set_route('List', 'Asset Maintenance Log', {
								'custom_hospital_name': '${location.name}',
								'maintenance_status': 'Planned'
							})">
							 Planned: ${location.planned_maintenance} ,
						</a>

    				
					<a href="javascript:void(0);" 
							style="color: green; font-weight: bold; text-decoration: none; cursor: pointer;"
							onclick="frappe.set_route('List', 'Asset Maintenance Log', {
								'custom_hospital_name': '${location.name}',
								'maintenance_status': 'Completed'
							})">
							 Completed: ${location.completed_maintenance} ,
						</a>
					
				
					
					<a href="javascript:void(0);"
                                                        style="color: red; font-weight: bold; text-decoration: none; cursor: pointer;"
                                                        onclick="frappe.set_route('List', 'Asset Maintenance Log', {
                                                                'custom_hospital_name': '${location.name}',
                                                                'maintenance_status': 'Overdue'
                                                        })">
                                                         Overdue: ${location.overdue_maintenance}
                                                </a>


                                        </div><br>
					<div class="view-assets">
						<button class="btn btn-xs btn-primary" 
							onclick="frappe.set_route('List', 'Asset', {'company': '${location.name}'})">
							View Assets
						</button>
						<button class="btn btn-xs btn-warning" 
							onclick="frappe.set_route('List', 'Work_Order', {'company': '${location.name}'})">
							View Work Orders
						</button>
						
					</div>
				</div>
			`;
	
			//marker.bindPopup(popupContent);

			// ✅ Decide popup direction dynamically
			marker.bindPopup(popupContent, {
				autoPan: true,              // ✅ Pan map if popup would overflow
				keepInView: true,           // ✅ Force popup to stay inside view
				closeButton: true,
				autoClose: false,
				//className: isRTL ? 'hospital-popup-container rtl-popup' : 'hospital-popup-container',
				className: 'hospital-popup-container',
				offset: [0, 25],            // ✅ Bias popup to appear below marker
				maxWidth: 300,
				maxHeight: 410,
				autoPanPaddingTopLeft: [20, 20],      // ✅ padding from top/left edge
				autoPanPaddingBottomRight: [20, 20]   // ✅ padding from bottom/right
			});

		/*	marker.bindPopup(popupContent, {
				autoPan: false,           // ✅ Don't auto-move map to other countries
				closeButton: true,       // ✅ Allow closing popup
				autoClose: false,        // ✅ Don't auto-close when clicking elsewhere
				className: 'hospital-popup-container',
				maxWidth: 300,           // ✅ Control popup width
				maxHeight: 400,          // ✅ Control popup height
				autoPanPadding: [10, 10] // ✅ Minimal padding if autoPan is needed
			});  */

			// Create tooltip for hover with urgent indicator
			const urgentIndicator = location.urgent_work_orders > 0 ? '🚨 URGENT! ' : '';

			//const rtlOffset = [-80, 0];  // Negative moves tooltip left in screen space

			marker.bindTooltip(`
				<div>
					<b>${urgentIndicator}${location.name}</b>
					<br>Assets: ${location.assets}
					<br><span style="color: black;  font-weight: bold; padding: 2px 4px;">Normal WOs: ${location.normal_work_orders}</span>
    				<br><span style="color: red;  font-weight: bold; padding: 2px 4px;">Urgent WOs: ${location.urgent_work_orders}</span>
					<br><span style="color: orange;  font-weight: bold; padding: 2px 4px;">Planned PMs: ${location.planned_maintenance}</span>
					<br><span style="color: green;  font-weight: bold; padding: 2px 4px;">Completed PMs: ${location.completed_maintenance}</span>
				</div>
			`, { className: 'hospital-tooltip',
				//offset: [-20, -20], 
				offset: isRTL ? [-20, -20] : [0, -20],
  direction: 'right'
				});
	
			bounds.extend([lat, lng]);
		});
	
		//if (locations.length > 0 && locations.some(l => l.latitude && l.longitude)) {
		//	this.map.fitBounds(bounds, { padding: [50, 50] });
		//}
		if (locations.length > 0 && locations.some(l => l.latitude && l.longitude)) {
    // ✅ Zoom into hospital bounds, but don’t zoom too much
    this.map.fitBounds(bounds, { padding: [30, 30], maxZoom: 8 });
} else {
    // ✅ Fallback: show Saudi Arabia center
    this.map.setView([24.8, 45.5], 6);
}

	}
	
}




