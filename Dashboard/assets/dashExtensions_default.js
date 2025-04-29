window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(e) {
            return [e.target.getLatLng().lat, e.target.getLatLng().lng];
        }
    }
});