var main = function() {
    var clock = new FlipClock($('.countdown'), {
        countdown = true;
    });
    
    clock.setTime(3600);
    clock.start();
};

$(document).ready(main);
