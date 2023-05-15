document.addEventListener('DOMContentLoaded', function() {
    var image = document.querySelector('.shake-image');

    function activateShake() {
        image.classList.add('shake-animation');
        setTimeout(function() {
            image.classList.remove('shake-animation');
        }, 1000);
    }
});
