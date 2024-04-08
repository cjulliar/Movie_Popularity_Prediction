document.addEventListener('DOMContentLoaded', function() {
    'use strict'

    document.querySelector('#menu-button').onclick = () => {
        showMenu();
        document.querySelector('#menu-button').style.borderColor = '#263547';
    }
});


function showMenu() {
    
    const menu_div = document.querySelector('#menu-div');
    const cross = document.querySelector('#cross');
    const background = document.querySelector('#background');
    const list = document.querySelector('#menu-list');

    menu_div.style.display = 'block';

    cross.onclick = () => {
        menu_div.style.display = 'none';
    }

    background.onclick = () => {
        menu_div.style.display = 'none';
    }
};