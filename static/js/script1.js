history.pushState(null, null, location.href);

window.addEventListener('popstate', (e) => {
    history.go(1);

});

// reloadを禁止する方法
// F5キーによるreloadを禁止する方法
document.addEventListener("keydown", function (e) {

    if ((e.which || e.keyCode) == 116) {
        e.preventDefault();
    }

});

$(window).on("beforeunload", function (e) {
    e.preventDefault();
    // e.returnValue = "本当にページを終了しますか？";
    return "本当にページを終了しますか？";
});

window.onload = function () {
    var image = document.getElementById("img");

    function updateImage() {
        image.src = image.src.split("?")[0] + "?" + new Date().getTime();
    }
    setInterval(updateImage, 60000);
}

function set2fig(num) {
    // 桁数が1桁だったら先頭に0を加えて2桁に調整する
    var ret;
    if (num < 10) { ret = "0" + num; }
    else { ret = num; }
    return ret;
}
function showClock2() {
    var nowTime = new Date();
    var nowHour = set2fig(nowTime.getHours());
    var nowMin = set2fig(nowTime.getMinutes());
    var nowSec = set2fig(nowTime.getSeconds());
    var msg = nowHour + ":" + nowMin + ":" + nowSec;
    document.getElementById("RealtimeClockArea2").innerHTML = msg;
}
setInterval('showClock2()', 1000);


let offsetX = 0
let offsetY = 0
var targetTop = document.getElementById('board');
var x = document.getElementById("devicex").value;
var y = document.getElementById("devicey").value;
var deviceID = document.getElementById("hiddendeviceID").value;
var temp = document.getElementById("temp").value;

window.onload = () => {
    // canvas準備
    const board = document.getElementById('board');
    const ctx = board.getContext("2d");

    ctx.translate(-63, -59);

    // 画像読み込み
    const chara = new Image();
    chara.src = "static\\images\\temperature_distribution_" + deviceID + ".png";
    chara.onload = () => {
        ctx.drawImage(chara, 0, 0);
        ctx.fillStyle = 'red';  // 塗りつぶしの色
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, 2 * Math.PI, false);
        ctx.fill();

        ctx.font = '12px Arial';
        ctx.fillStyle = '#000000';
        ctx.fillText(temp + "℃", x, y - 10);
    };

    function updateImage() {
        chara.src = chara.src.split("?")[0] + "?" + new Date().getTime();
    }
    setInterval(updateImage, 60000);

    // targetTop.addEventListener('click', function (e) {
    //     offsetX = e.offsetX; // =>要素左上からのx座標
    //     offsetY = e.offsetY; // =>要素左上からのy座標

    //     // 青い三角形を描く
    //     ctx.beginPath();
    //     ctx.fillStyle = 'blue';
    //     ctx.moveTo(offsetX + 75, offsetY + 71 - 5);
    //     ctx.lineTo(offsetX + 75 - 5, offsetY + 71 + 5);
    //     ctx.lineTo(offsetX + 75 + 5, offsetY + 71 + 5);
    //     ctx.closePath();
    //     ctx.fill();

    //     x0 = 637
    //     y0 = 756
    //     offsetX = offsetX * x0 / 373
    //     offsetY = offsetY * y0 / 463

    //     offsetX = Math.round(offsetX)
    //     offsetY = Math.round(offsetY)

    //     // ctx.clearRect(offsetX - 5, offsetY - 5, 10, 10);

    //     // ctx.fillStyle = '#000';
    //     // ctx.fillRect(offsetX - 5, offsetY - 5, 10, 10);

    //     // document.getElementById('x').textContent = 'x : ' + offsetX;
    //     // document.getElementById('y').textContent = 'y : ' + offsetY;
    //     document.getElementById('hiddenx').value = offsetX;
    //     document.getElementById('hiddeny').value = offsetY;
};



