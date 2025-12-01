// admin_set_latlng.js
// Скрипт для admin change/add: если в URL есть ?lat=...&lng=... — подставляет в поля.
// Также слушает postMessage от iframe map-picker.

(function() {
  function getQueryParams() {
    var qs = location.search.substring(1);
    var parts = qs.split('&');
    var res = {};
    parts.forEach(function(p){
      if (!p) return;
      var kv = p.split('=');
      try {
        res[decodeURIComponent(kv[0])] = decodeURIComponent(kv[1] || '');
      } catch(e){}
    });
    return res;
  }

  function setLatLng(lat, lng) {
    if (!lat || !lng) return;
    var latEl = document.getElementById('id_lat');
    var lngEl = document.getElementById('id_lng');
    if (latEl) latEl.value = lat;
    if (lngEl) lngEl.value = lng;
    // trigger change for widgets
    if (typeof jQuery !== 'undefined') {
      jQuery('#id_lat').trigger('change');
      jQuery('#id_lng').trigger('change');
    }
  }

  document.addEventListener('DOMContentLoaded', function(){
    // 1) если в URL есть lat & lng - сразу вставляем
    var q = getQueryParams();
    if (q.lat && q.lng) {
      setLatLng(q.lat, q.lng);
    }

    // 2) слушаем сообщения из iframe
    window.addEventListener('message', function(event){
      try {
        var data = event.data || {};
        if (data.type === 'coords_selected') {
          setLatLng(data.lat, data.lng);
          // Опционально: всплыть сообщение
          var el = document.getElementById('id_lat');
          if (el) el.focus();
        }
      } catch(err) { console.error(err); }
    }, false);
  });
})();
