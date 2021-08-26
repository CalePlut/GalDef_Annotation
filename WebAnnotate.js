document.addEventListener('keydown', keyPress)

var change = false;
var time = 0.0;
var annot = 0.0;
var chart;
var affectData = [["Time","Rating"]];
var playing = false;
var vid = document.getElementById("annot_target");
var annotating=true;
var myVideo ="";
var dimension = window.sessionStorage.getItem("Dimension");
var conditions=["Linear", "Adaptive", "Generative", "None"];
var condition;
var overlay = false;

const labels=[0.25]
const data = {
    labels: labels,
    datasets: [{
        label: capitalizeFirstLetter(dimension),
        backgroundColor: 'rgb(255,0, 0)',
        borderColor: 'rgb(255,255,255)',
        borderWidth: '1',
        pointRadius:'1',
        color:'rgb(255,255,255)',
        data: [0],
    }]
};

const config = {
    type: 'line', data,
    options: { responsive: true,
        padding:20       
    }
};

//Setup
function annotation_setup() {
    raiseOverlay(conditions.length);
    condition = select_condition();
    console.log("Condition =" + condition);
    console.log("Dimension = " + dimension);
    console.log("Starting annotation");
    vid = document.getElementById("annot_target");
    var toVideo = "GalDefSample.mp4";
    vid.src=toVideo;
    setup_chart();
}
function setup_chart() {
    chart = new Chart(document.getElementById('affect_chart'), config);
}

//Returns the selected condition and prunes list
function select_condition(){
    var which_condition = Math.floor(Math.random()*conditions.length);
    var condition = conditions[which_condition];
    conditions.splice(which_condition, 1);
    return condition;
}

function begin_annotate(){
    lower_overlay();
    playing=true;
    vid.play();
    annotate_video();
}
function pause_annotate(){
    playing=false;
    vid.pause();
}

function raiseOverlay(remaining_conditions){
    if(remaining_conditions==4){
        document.getElementById("begin").style ="display:block";
    }
    else if (remaining_conditions>0){
        document.getElementById("between").style= "display:block";
    }
    else{
        document.getElementById("finished").style="display:block";
    }
}

function lower_overlay(){
    document.getElementById("begin").style ="display:none";
    document.getElementById("between").style= "display:none";
    document.getElementById("finished").style="display:none";
}

function end_annotate(){
    //First, export the annotation to the php file
    annotating=false;
    export_csv("Annotate_GalDef", affectData, ",", "Annotate_GalDef");
}

const export_csv = (arrayHeader, data, delimiter, fileName) => {
    var csv = '\"';
    csv+=arrayHeader;
    csv+=vid.baseURI;
    csv+="\r\n";
    data.forEach(function(row) {
        csv += row.join(',');
        csv += "\r\n";
    });

    let hiddenElement = document.createElement('a');
    hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);
    hiddenElement.target = '_blank';
    hiddenElement.download = fileName + '.csv';
    //hiddenElement.click();    !!!!!!!For now we don't save, maybe add.
}

function post_CSV () {
    console.log("Posting CSV");
    var csv="Timestamp,Annotation\r\n"
    //First, do all of the data stuff
    csv+="\r\n";
    affectData.forEach(function(row) {
        csv += row.join(",");
        csv += "\r\n";
    });


    // (A) CREATE BLOB OBJECT
    var myBlob = new Blob([csv], {type: "text/csv"});
  
    // (B) FORM DATA
    var data = new FormData();
    data.append("upfile", myBlob);

    // (C) AJAX UPLOAD TO SERVER
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "uploadCSV.php");
    xhr.onload = function () {
      console.log(this.status);
      console.log(this.response);
    };
    xhr.send(data);
  }




//Load video and begin time-code watching
function load_video() {

}

//Every .25 seconds, record the current level of affect dimension into a list w. timecode
function annotate_video() {
    //Update time
    time += 0.25;
    //Reset change variable
    if (change == true) {
        change = false;
    }
    //Updates chart
    update_chart();
    //Re-run every 250 ms, which is our window
    if(playing){
    setTimeout(annotate_video, 250);}

}

function update_chart() {
    console.log("Time:" + time + ", annot: "+annot);
    affectData.push([time, annot])
    let all_labels=data.labels;
    all_labels.push(time);
    data.labels=all_labels;
    data.datasets[0].data.push(annot);
    chart.update();
}


function keyPress(e) {
    //console.log("Key press detected");
    if (change == false) {
        toChange = 0;

        if (e.code == "ArrowUp") {
            toChange = 1;
            change = true;
        } 
        else if (e.code == "ArrowDown") {
            toChange = -1;
            change = true;
        }
        else if (e.code=="Space"){
            if(!playing){
                begin_annotate();
            }
            else{pause_annotate();}
        }

        annot += toChange;
        //console.log(dimension);
    }


}

function capitalizeFirstLetter(string){return string.charAt(0).toUpperCase() + string.slice(1);}