function openMapModal(latFieldId, lngFieldId) {
    window.latField = document.getElementById(latFieldId);
    window.lngField = document.getElementById(lngFieldId);

    const modal = document.getElementById("modal-bg");
    modal.style.display = "block";

    if (!window.leafletMapLoaded) {
        window.leafletMapLoaded = true;
        setTimeout(initMap, 100);
    }
}

function closeMapModal() {
    document.getElementById("modal-bg").style.display = "none";
}
