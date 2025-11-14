(function (exports) {
    'use strict';

    function buildSentinelLayer() {
        return L.tileLayer('https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/GoogleMapsCompatible/{z}/{y}/{x}.jpg', {
            attribution: 'Imagery &copy; <a href="https://eox.at" target="_blank" rel="noopener">EOX IT Services GmbH</a> &middot; Datos Copernicus Sentinel modificados',
            maxZoom: 18
        });
    }

    function buildOsmLayer() {
        return L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
            subdomains: 'abc'
        });
    }

    function buildRoadsOverlay() {
        return L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}.png', {
            attribution: 'Cartografía base &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a> &middot; Datos &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
            subdomains: 'abcd',
            opacity: 0.5,
            maxZoom: 19
        });
    }

    function buildLabelsOverlay() {
        return L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}.png', {
            attribution: 'Calles y etiquetas &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener">CARTO</a> &middot; Datos &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
            subdomains: 'abcd',
            maxZoom: 20
        });
    }

    function createBaseLayers() {
        return {
            'Satélite (Sentinel-2)': buildSentinelLayer(),
            'Cartografía OSM': buildOsmLayer()
        };
    }

    function createOverlayLayers() {
        return {
            'Rutas OSM': buildRoadsOverlay(),
            'Etiquetas OSM': buildLabelsOverlay()
        };
    }

    function applyDefaultLayers(map, options) {
        if (!map || typeof L === 'undefined') {
            return { baseLayers: {}, overlayLayers: {}, control: null };
        }

        const opts = Object.assign({
            collapsedControl: true,
            defaultBaseKey: 'Satélite (Sentinel-2)',
            defaultOverlays: ['Rutas OSM', 'Etiquetas OSM'],
            attributionPrefix: ''
        }, options);

        const baseLayers = createBaseLayers();
        const overlayLayers = createOverlayLayers();

        if (map.attributionControl && typeof map.attributionControl.setPrefix === 'function') {
            map.attributionControl.setPrefix(opts.attributionPrefix);
        }

        const defaultBaseLayer = baseLayers[opts.defaultBaseKey];
        if (defaultBaseLayer) {
            defaultBaseLayer.addTo(map);
        }

        opts.defaultOverlays.forEach((key) => {
            const layer = overlayLayers[key];
            if (layer) {
                layer.addTo(map);
            }
        });

        const control = L.control.layers(baseLayers, overlayLayers, {
            collapsed: opts.collapsedControl
        }).addTo(map);

        return { baseLayers, overlayLayers, control };
    }

    exports.createBaseLayers = createBaseLayers;
    exports.createOverlayLayers = createOverlayLayers;
    exports.applyDefaultLayers = applyDefaultLayers;
})(window.TrazappMaps = window.TrazappMaps || {});
