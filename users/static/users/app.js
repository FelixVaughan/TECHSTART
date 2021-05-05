'use strict'

const slider = document.getElementById("myRange");
const output = document.getElementById("demo");

function openForm() {
        document.getElementById("popupForm").style.display = "block";
    }
function closeForm() {
        document.getElementById("popupForm").style.display = "none";
    }

function spotifyTop(){
    console.log('spotify_top')
    $.get('ajax/?social=spotify_top', function (data) {
        $("#ajax_spotify").html(data);
    })
}

function spotifyPlay(){
    console.log('spotify_play')
    $.get('song/?state=spotify_play', function (data) {
        $("#ajax_spotify_song").html(data);
    })
}

function spotifyPause(){
    console.log('spotify_pause')
    $.get('song/?state=spotify_pause', function (data) {
        $("#ajax_spotify_song").html(data);
    })
}

function spotifyShuffle(){
    console.log('spotify_shuffle')
    $.get('song/?state=spotify_shuffle', function (data) {
        $("#ajax_spotify_song").html(data);
    })
}

function spotifyNext(){
    console.log('spotify_next')
    $.get('song/?state=spotify_next', function (data) {
        $("#ajax_spotify_song").html(data);
    })
}

function spotifyPrev(){
    console.log('spotify_prev')
    $.get('song/?state=spotify_prev', function (data) {
        $("#ajax_spotify_song").html(data);
    })
}

function spotifyPlayer(){
    document.getElementById("SpotifyPlayer").style.display = "block";
}

output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  output.innerHTML = this.value;
  console.log("slider")
  $.get('song/?volume=' + this.value)
}

function spotifyOpen() {
    document.getElementById("Spotify").style.display = "block";
    closeForm();
    console.log('spotify')
    $.get('ajax/?social=spotify_init')
}

function spotifyClose() {
    document.getElementById("Spotify").style.display = "none";
    $.get('song/?state=spotify_pause')
    }

    
function redditData() {
        document.getElementById("Reddit").style.display = "block";
        closeForm();
        console.log('reddit data')
        $.get('reddit/?state=redditData')
        }

function redditOpen() {
    document.getElementById("Reddit").style.display = "block";
    closeForm();
    console.log('reddit open')
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
    $.get('article/')
    }

function newsClose() {
    document.getElementById("News").style.display = "none";
    }

function toggle_light_mode() {
    var app = document.getElementsByTagName("BODY")[0];
    if (localStorage.lightMode == "dark") {
        localStorage.lightMode = "light";
        app.setAttribute("light-mode", "light");
        } else {
        localStorage.lightMode = "dark";
        app.setAttribute("light-mode", "dark");
        }
    }