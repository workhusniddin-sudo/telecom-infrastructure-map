function openMapPicker() {
    document.getElementById("map-modal").style.display = "block";

    setTimeout(() => {
        if (!window.mapLoaded) {
            window.mapLoaded = true;

            var map = L.map("map-picker").setView([40.2833, 69.6167], 13);

            L.tileLayer(
                "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{x}/{y}",
                {
                    maxZoom: 19,
                    attribution: "Tiles © Esri"
                }
            ).addTo(map);

            var marker;

            map.on("click", function (e) {
                let lat = e.latlng.lat.toFixed(6);
                let lng = e.latlng.lng.toFixed(6);

                document.getElementById("id_lat").value = lat;
                document.getElementById("id_lng").value = lng;

                if (marker) map.removeLayer(marker);
                marker = L.marker([lat, lng]).addTo(map);

                closeMapPicker();
            });
        }
    }, 300);
}

function closeMapPicker() {
    document.getElementById("map-modal").style.display = "none";
}
