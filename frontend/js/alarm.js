// instead of hardcoding, use address which browser accessed Pico W.
const PicoAddress = window.location.href

const getData = async () => {
    // send GET request to Pico Address to fetch recent PIR sensor data"
    const data = await fetch(`${PicoAddress}data`);
    // response is a string, so data.text() decodes the Response's body
    const counter = await data.text();
    const passenger = document.getElementById("passenger")
    //target passenger id and change its inner HTML to counter, which is the number of passengers
    passenger.innerHTML = `${counter}`;
    //run getData() on an interval
    setInterval(getData,100)
};
// when the button is pressed, send GET request to pico with URL parameters alarm=on
const startAlarm = async () => {
    const action = await fetch(`${PicoAddress}alarm=on`);
};

getData();
