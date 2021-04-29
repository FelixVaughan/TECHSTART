'use strict'

const switcher = document.querySelector('.block');
const appInit = document.querySelector('.btn');

appInit.addEventListener('click', function() {
    document.getElementById("container").style.display = "block";
    $('.box').append('<div class="container p-3 my-3 border"></div>'); //append container
    });

function openForm() {
        document.getElementById("popupForm").style.display = "block";
    }
function closeForm() {
        document.getElementById("popupForm").style.display = "none";
    }

function spotifyOpen() {
    document.getElementById("Spotify").style.display = "block";
    closeForm();
    }


function redditOpen() {
    document.getElementById("Reddit").style.display = "block";
    closeForm();
    }


function outlookOpen() {
    document.getElementById("Outlook").style.display = "block";
    closeForm();
    }

function newsOpen() {
    document.getElementById("News").style.display = "block";
    closeForm();
    }