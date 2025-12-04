
/*$(document).ready(function () {
    const widgetNames = ["eh0tdvlmin","goctvitvje","fjbi1qp64g","6v10o9c31q","7sgvfh9372"];
    const iframeHTML = `
        <div style="height:800px; overflow:hidden; border-radius: 8px; box-shadow: 0 0 4px #ccc;">
            <iframe src="/standalone-active-map" style="width:100%; height:80%; border:none;"></iframe>
        </div>
    `;

    // Wait for dashboard to load
    setTimeout(function () {
        widgetNames.forEach(widgetName => {
            $(`div[data-widget-name="${widgetName}"]`).each(function () {
                const $chartContainer = $(this).find('.chart-container, .frappe-chart');
                if ($chartContainer.length) {
                    $chartContainer.html(iframeHTML);
                }
            });
        });
    }, 2000);
});
*/

function runMapInjectionScript() {
    const targetTitle = "Active Map Chart";
    const iframeHTML = `
        <div style="height:500px; width:95%; overflow:hidden; border-radius: 8px; box-shadow: 0 0 4px #ccc;">
            <iframe src="/standalone-active-map" style="width:100%; height:100%; border:none;"></iframe>
        </div>
    `;

    function injectMap(retryCount = 0) {
        let injected = false;

        $('div.widget.dashboard-widget-box').each(function () {
            const $widget = $(this);
            const title = $widget.find('.widget-title span.ellipsis').text().trim();

            console.log("Found widget title:", title);

            if (title === targetTitle) {
                const $chartContainer = $widget.find('.chart-container, .frappe-chart');

                console.log("→ Checking chart container for:", title);
                console.log("→ Chart container found:", $chartContainer.length);
                console.log("→ Already injected:", $chartContainer.hasClass("map-injected"));

                if ($chartContainer.length && !$chartContainer.hasClass("map-injected")) {
                    $chartContainer.addClass("map-injected").html(iframeHTML);
                    console.log("✅ Map injected into:", title);
                    injected = true;
                }
            }
        });

        if (!injected && retryCount < 10) {
            setTimeout(() => injectMap(retryCount + 1), 500);
        }
    }

    injectMap();

    // Optionally reinject on dashboard refresh
    $(document).on('dashboard-refresh', injectMap);
}

// Run on first load
$(document).ready(runMapInjectionScript);

// Also run when navigating via search or sidebar
frappe.router.on('change', function () {
    // Small delay to let new page render
    setTimeout(() => {
        runMapInjectionScript();
    }, 300);
});



/*$(document).ready(function () {
    const targetTitle = "Active Map Chart";
    const iframeHTML = `
        <div style="height:500px; width:95%; overflow:hidden; border-radius: 8px; box-shadow: 0 0 4px #ccc;">
            <iframe src="/standalone-active-map" style="width:100%; height:100%; border:none;"></iframe>
        </div>
    `;

    function injectMap(retryCount = 0) {
        let injected = false;

        $('div.widget.dashboard-widget-box').each(function () {
            const $widget = $(this);
            const title = $widget.find('.widget-title span.ellipsis').text().trim();
		console.log("Found widget title:", title);

            if (title === targetTitle) {
                const $chartContainer = $widget.find('.chart-container, .frappe-chart');
		    console.log("→ Checking chart container for:", title);
            	console.log("→ Chart container found:", $chartContainer.length);
            	console.log("→ Already injected:", $chartContainer.hasClass("map-injected"));

                if ($chartContainer.length && !$chartContainer.hasClass("map-injected")) {
                    $chartContainer.addClass("map-injected").html(iframeHTML);
                    injected = true;
                }
            }
        });

        if (!injected && retryCount < 10) {
            setTimeout(() => injectMap(retryCount + 1), 500);
        }
    }

    injectMap();

});
*/
