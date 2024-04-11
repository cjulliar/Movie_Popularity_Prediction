document.addEventListener('DOMContentLoaded', function() {
    'use strict'

    document.querySelector('#menu-button').onclick = () => {
        showMenu();
    }
})


function showMenu() {
    
    let menu_div = document.querySelector('#menu-div');
    let cross = document.querySelector('#cross');
    let back = document.querySelector('#back');

    menu_div.style.display = 'block';

    cross.onclick = () => {
        menu_div.style.display = 'none';
    }

    back.onclick = () => {
        menu_div.style.display = 'none';
    }
}