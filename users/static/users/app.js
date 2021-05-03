'use strict'

/*
const switcher = document.querySelector('.block');
const appInit = document.querySelector('.btn');
appInit.addEventListener('click', function() {
    document.getElementById("container").style.display = "block";
    $('.box').append('<div class="container p-3 my-3 border"></div>'); //append container
    });
*/
function openForm() {
        document.getElementById("popupForm").style.display = "block";
    }
function closeForm() {
        document.getElementById("popupForm").style.display = "none";
    }

function spotifyTop(){
    console.log('spotify_top')
    $.get('ajax/?social=spotify_top', function (data) {
        $("#ajax_spotify").append(data);
    })
}

function spotifyPlay(){
    console.log('spotify_play')
    $.get('ajax/?social=spotify_play', function (data) {
        $("#ajax_spotify").append(data);
    })
}

function spotifyPause(){
    console.log('spotify_pause')
    $.get('ajax/?social=spotify_pause', function (data) {
        $("#ajax_spotify").append(data);
    })
}

function spotifyShuffle(){
    console.log('spotify_shuffle')
    $.get('ajax/?social=spotify_shuffle', function (data) {
        $("#ajax_spotify").append(data);
    })
}

function spotifyNext(){
    console.log('spotify_next')
    $.get('ajax/?social=spotify_next', function (data) {
        $("#ajax_spotify").append(data);
    })
}

function spotifyPrev(){
    console.log('spotify_prev')
    $.get('ajax/?social=spotify_prev', function (data) {
        $("#ajax_spotify").append(data);
    })
}

function spotifyPlayer(){
    document.getElementById("SpotifyPlayer").style.display = "block";
}

function spotifyOpen() {
    document.getElementById("Spotify").style.display = "block";
    closeForm();
    console.log('spotify')
    $.get('ajax/?social=spotify_init')
}

function spotifyClose() {
    document.getElementById("Spotify").style.display = "none";
    }

function redditOpen() {
    document.getElementById("Reddit").style.display = "block";
    closeForm();
    console.log('reddit')
    $.get('ajax/?social=reddit')
    }

function redditClose() {
    document.getElementById("Reddit").style.display = "none";
    }

function outlookClose() {
    document.getElementById("Outlook").style.display = "none";
    }

function outlookOpen() {
    document.getElementById("Outlook").style.display = "block";
    closeForm();
    }

function newsOpen() {
    document.getElementById("News").style.display = "block";
    closeForm();
    }

function newsClose() {
    document.getElementById("News").style.display = "none";
    }