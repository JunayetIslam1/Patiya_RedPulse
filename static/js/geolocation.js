(function () {
    function bindLocateButton(btn) {
        btn.addEventListener('click', function () {
            if (!navigator.geolocation) {
                btn.textContent = 'Geolocation not supported';
                return;
            }
            var original = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Locating…';
            navigator.geolocation.getCurrentPosition(function (pos) {
                var latInput = document.getElementById(btn.dataset.latTarget);
                var lngInput = document.getElementById(btn.dataset.lngTarget);
                if (latInput) latInput.value = pos.coords.latitude;
                if (lngInput) lngInput.value = pos.coords.longitude;
                btn.classList.add('is-set');
                btn.innerHTML = '<i class="fas fa-check"></i> ' + (btn.dataset.successLabel || 'Location set');
                if (btn.dataset.autoSubmit === 'true') {
                    btn.closest('form').submit();
                }
            }, function () {
                btn.innerHTML = original;
                alert(btn.dataset.errorLabel || 'Could not get your location. Please allow location access and try again.');
            }, { timeout: 10000 });
        });
    }

    document.querySelectorAll('.locate-btn').forEach(bindLocateButton);
})();
