document.addEventListener('DOMContentLoaded', function() {
    'use strict'

    document.querySelectorAll('#result').forEach(result => {
        if (result.dataset.result < 0) {
            result.style.color = "Red";
        }
        else if (result.dataset.result > 0) {
            result.style.color = "SeaGreen";
        }
    })
})