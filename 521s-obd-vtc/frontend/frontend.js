var socket = io.connect('http://54.186.6.245:5000');

$(document).ready(function() {

    //-----------------------------------//
    //----- Socket Stuff Here -----------//
    //-----------------------------------//
    socket.on('connected', function(msg) {
       console.log('connected', msg);
   });

    socket.on('publish', function(msg) {
        var data = JSON.parse(msg)
        modifiyMarker(data.latitude, data.longitude)
        speedometer.set(data.speed)
        tachometer.set(data.rpm)
        throttlegauge.set(data['throttle position'])
        if (data.anomalies.length != 0){
            console.log(data.anomalies)    
            registerAnomalies(data.anomalies)
            setAnomalyMarker(data)
        }
    });

    //-----------------------------------//
    //----- Init History Stuff Here -----//
    //-----------------------------------//

    findVehicles()
    
    //-----------------------------------//
    //----- Gauge Canvas Opts -----------//
    //-----------------------------------//
    var speedopts = {
       angle: 0, 
       lineWidth: 0.2, 
       radiusScale: 1, 
       pointer: {
          length: 0.6, 
          strokeWidth: 0.035, 
          color: '#000000' 
       },
       limitMax: false,     
       limitMin: false,     
       colorStart: '#6FADCF',   
       colorStop: '#8FC0DA',    
       strokeColor: '#E0E0E0',  
       generateGradient: true,
       highDpiSupport: true,    
       renderTicks: {
            divisions: 5,
            divWidth: 1.1,
            divLength: 0.7,
            divColor: '#333333',
            subDivisions: 3,
            subLength: 0.5,
            subWidth: 0.6,
            subColor: '#666666'
        },
       staticLabels: {
            font: "12px sans-serif",  // Specifies font
            labels: [10, 20, 30, 40, 50, 60, 70, 80 , 90 ,100], 
            color: "#000000",  
            fractionDigits: 0  
        },
        staticZones: [
            {strokeStyle: "#30B32D", min: 0, max: 80},
            {strokeStyle: "#F03E3E", min: 80, max: 100} 
        ],
        renderTicks: {
            divisions: 10,
            divWidth: 1.1,
            divLength: 0.7,
            divColor: "#333333",
            subDivisions: 2,
            subLength: 0.5,
            subWidth: 0.6,
            subColor: "#666666"
        }
    };

    var RPMopts = {
        angle: 0, 
        lineWidth: 0.3, 
        radiusScale: 1, 
        pointer: {
          length: 0.6, 
          strokeWidth: 0.035, 
          color: '#000000' 
        },
        limitMax: false,     
        limitMin: false, 
        colorStart: '#6F6EA0',  
        colorStop: '#C0C0DB',   
        strokeColor: '#EEEEEE', 
        generateGradient: true,
        highDpiSupport: true,   
        renderTicks: {
          divisions: 8,
          divWidth: 1.1,
          divLength: 0.7,
          divColor: '#333333',
          subDivisions: 2,
          subLength: 0.5,
          subWidth: 0.6,
          subColor: '#666666'
        },
        staticLabels: {
            font: "12px sans-serif",  
            labels: [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000],  
            color: "#000000",  
            fractionDigits: 0  
        },
        staticZones: [
            {strokeStyle: "#30B32D", min: 0, max: 5000}, 
            {strokeStyle: "#FFDD00", min: 5000, max: 6500}, 
            {strokeStyle: "#F03E3E", min: 6500, max: 8000}  
        ]
      };

    var Throttleopts = {
        angle: -0.46 , 
        lineWidth: 0.06, 
        radiusScale: 1, 
        pointer: {
          length: 0.4, 
          strokeWidth: 0.066, 
          color: '#000000' 
        },
        limitMax: false,     
        limitMin: false,    
        colorStart: '#CF0000',   
        colorStop: '#DA0000',    
        strokeColor: '#E0E0E0',  
        generateGradient: true,
        highDpiSupport: true,
        renderTicks: {
            divisions: 5,
            divWidth: 1.1,
            divLength: 0.7,
            divColor: '#333333',
            subDivisions: 0,
            subLength: 0.5,
            subWidth: 0.6,
            subColor: '#666666'
          },
        staticLabels: {
            font: "12px sans-serif",  
            labels: [0, 20, 40, 60, 80,100],  
            color: "#000000",  
            fractionDigits: 0  
        },     
    };

    var rpmtarget = document.getElementById('rpm'); 
    var tachometer = new Gauge(rpmtarget).setOptions(RPMopts); 
    tachometer.maxValue = 8000; 
    tachometer.setMinValue(0);  
    tachometer.animationSpeed = 500; 
    tachometer.set(0); 


    var speedtarget = document.getElementById('speed');
    var speedometer = new Gauge(speedtarget).setOptions(speedopts);
    speedometer.maxValue = 100;
    speedometer.setMinValue(0);
    speedometer.animationSpeed = 500; 
    speedometer.set(0);

    var throttletarget = document.getElementById('throttle'); 
    var throttlegauge = new Gauge(throttletarget).setOptions(Throttleopts);
    throttlegauge.maxValue = 100;
    throttlegauge.setMinValue(0);
    throttlegauge.animationSpeed = 500;
    throttlegauge.set(0); 
});



//-----------------------------------------------------------------//
// Map Stuff here -------------------------------------------------//
//-----------------------------------------------------------------// 
var map;
var vehicleMarker;
var centerCounter = 0
var anomalyCounter = 1
function initialize() 
{
    var mapOptions = {center: new google.maps.LatLng(38.766943, -90.500801), zoom: 16}
    map = new google.maps.Map(document.getElementById("map"), mapOptions)
    vehicleMarker = new google.maps.Marker({
        icon: {   
            url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
        }
    });

    vehicleMarker.setMap(map)

}

google.maps.event.addDomListener(window, 'load', initialize);


function modifiyMarker(latitude, longitude){
    if (centerCounter%10 == 0) {
        
        reCenterMap({lat: parseFloat(latitude), lng: parseFloat(longitude)})
    } 

    vehicleMarker.setPosition({lat: parseFloat(latitude), lng:  parseFloat(longitude)})
    centerCounter = centerCounter + 1
}

function reCenterMap(latLng){
    map.setCenter(latLng)
    map.setZoom(16)

}


//-----------------------------------------------------------------//
// Driving Histories Stuff Here -----------------------------------//
//-----------------------------------------------------------------// 
var routeHolder = new Object();
var polyHolder = new Object();

function findVehicles(){
    var flag = "vehicles"
    getRequest(flag) //async
}


function findHistories(VIN){
    getRequest(VIN) //async
}

function populateVehicleList(data){
    var node = document.getElementById("vehicles")
    var obj = JSON.parse(data)
    obj.collections.forEach(vehicle => {
        var listElm = document.createElement("a")
        listElm.className = "list-group-item list-group-item-action"
        listElm.text = vehicle
        listElm.onclick = function() {findHistories(vehicle)}
        node.appendChild(listElm)
    });   
}

function populateHistoryList(history){
    //Get handle, clear out old routes from previous VIN
    var node = document.getElementById("histories")
    while (node.firstChild){
        node.removeChild(node.lastChild)
    }
        // ------------ Refresh Universal holder --------- //
    routeHolder = new Object();
    var obj = JSON.parse(history)
    
    obj.data.forEach(route => {
        // ----------- Handle Element Creation ------------//
        var check_id = route.start_time + "_check" 
        var color_id = route.start_time + "_color" 
        var listElm = document.createElement("a")
        var color = document.createElement("input")
        var check = document.createElement("input")
        // -----------  Element dynamic Styling ------------//
        color.setAttribute("type", "color")
        color.setAttribute("id", color_id)
        color.style["margin-left"] = "5px"
        color.addEventListener("change", function(){setColor(this.id)})
        check.className = "boxClass"
        check.setAttribute("type", "checkbox")
        check.setAttribute("id", check_id)
        
        check.onclick = function() {routeDrawer(this)}
        // ----------- Setting List Parameters ------------//
        listElm.className = "list-group-item list-group-item-action"
        listElm.innerText = route.start_time
        listElm.appendChild(check)
        listElm.appendChild(color)
        node.appendChild(listElm)
        // ------- Place Point Data in Universal Holder ----//
        routeHolder[route.start_time] = route.route_data 
    });
}

function routeDrawer(route){
    var r_id = route.id.replace("_check", '') //Pull routeholder id - sort of wonk but it works
    if (route.checked){ // Need to draw polyline
        var data = routeHolder[r_id]
        var coordinates = []
        data.forEach(entry => {
            coordinates.push({lat: Number(entry.latitude), lng: Number(entry.longitude)})
        });

        polyHolder[r_id] = new google.maps.Polyline({
            path: coordinates,
            geodesic: true,
            strokeColor: setColor(r_id),
            strokeOpacity: 1.0,
            strokeWeight: 2,
          });
          polyHolder[r_id].setMap(map);
    }

    else {
        
        polyHolder[r_id].setMap(null)
        delete polyHolder[r_id]
    }
}

function setColor(sender_id){
    if (!(String(sender_id).includes("_color"))) { //coming from check
        var color = document.getElementById(sender_id +"_color").value  
        return color
    } else { //coming from color picker
        var r_id = sender_id.replace("_color", '')
        if (polyHolder[r_id]) {
            // ----- New data reload ----- //
            var data = routeHolder[r_id]
            var coordinates = []
            data.forEach(point => {
                coordinates.push({lat: Number(point.latitude), lng: Number(point.longitude)})
            });
            polyHolder[r_id].setMap(null)
            delete polyHolder[r_id]  
            // ---- Generate New Poly ---- //
            polyHolder[r_id] = new google.maps.Polyline({
                path: coordinates,
                geodesic: true,
                strokeColor: document.getElementById(r_id + "_color").value,
                strokeOpacity: 1.0,
                strokeWeight: 2,
              });
            polyHolder[r_id].setMap(map)
       
        }
    }
}


//-----------------------------------------------------------------//
// API Utilities --------------------------------------------------//
//-----------------------------------------------------------------// 
function getRequest(flag){
    var xmlHttp = new XMLHttpRequest();
    if (flag == "vehicles"){
        xmlHttp.onreadystatechange = function() { 
            if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
                populateVehicleList(xmlHttp.responseText)
        }

        xmlHttp.open("GET", "http://54.186.6.245:5000/collection", true);
        xmlHttp.send(null);

    }
    else {
        var URL = "http://54.186.6.245:5000/histories/" + flag //where flag == VIN
        xmlHttp.onreadystatechange = function() { 
            if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
                populateHistoryList(xmlHttp.responseText)
        }
        xmlHttp.open("GET", URL, true);
        xmlHttp.send(null);
    }
}

function uncheck(id){
    var boxes = document.getElementsByClassName("boxGroup")
    
    for(i=0;i<boxes.length; i++){
        if(boxes[i].id != id){
            boxes[i].checked = false
        }
    }
}

//-----------------------------------------------------------------//
// Anomaly Detection Stuff here -----------------------------------//
//-----------------------------------------------------------------// 
var anomalyMarkers = []

function registerAnomalies(anomalies){
    anomalies.forEach(anomaly => {
        switch(anomaly) {
            case "Front Impact":
                var elm = document.getElementById("front")
                elm.style.backgroundColor = "red";
                break;
            case "Rear Impact":
                var elm = document.getElementById("rear")
                elm.style.backgroundColor = "red";
                break;
            case "Left Impact":
                var elm = document.getElementById("left")
                elm.style.backgroundColor = "red";
                break;
            case "Right Impact":
                var elm = document.getElementById("right")
                elm.style.backgroundColor = "red";
                break;
            default:
                console.log("N/A Anomaly Detection")
          }
    });
}

function resetImpacts(){
    document.getElementById("front").style.backgroundColor = "green";
    document.getElementById("rear").style.backgroundColor = "green";
    document.getElementById("left").style.backgroundColor = "green";
    document.getElementById("right").style.backgroundColor = "green";
}
function setAnomalyMarker(data){
    var lat = parseFloat(data.latitude)
    var lng = parseFloat(data.longitude)
    
    var anomalyMarker = new google.maps.Marker({
        icon: {   
            url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
        }
    });
    var contentString = '<h1 id="firstHeading" class="firstHeading">Impact Event</h1>' + '<div id="bodyContent">' +
    "<p>"+ data.anomalies[0] +"</p></div>";
    
    var infowindow = new google.maps.InfoWindow({
        content: contentString,
        maxWidth: 200,
      });

    anomalyMarker.addListener("click", () => {
        infowindow.open(map, anomalyMarker);
      });
    
    
    anomalyMarker.setPosition({lat: lat, lng:  lng})
    anomalyMarker.setMap(map)
    anomalyMarkers.push(anomalyMarker)

}

function clearAnomalies(){
    anomalyMarkers.forEach(marker => {
        marker.setMap(null)
    });

}