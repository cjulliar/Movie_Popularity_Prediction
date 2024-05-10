document.addEventListener('DOMContentLoaded', function() {
    'use strict'

    document.querySelectorAll('#film-preview').forEach(preview => {
        preview.onclick = () => {
            let id_preview = preview.dataset.pk;
            showInfo(id_preview);
        };
    })
})


function showInfo(id_preview) {

    let full_view = document.querySelector(`#full-${id_preview}`);
    let cross = document.querySelector(`#cross-${id_preview}`);
    let back = document.querySelector(`#back-${id_preview}`);

    full_view.style.display = 'block';

    cross.onclick = () => {
        full_view.style.display = 'none';
    };

    back.onclick = () => {
        full_view.style.display = 'none';
    };
}