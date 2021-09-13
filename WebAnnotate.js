document.addEventListener('keydown', keyPress)

var post_online = true;
var save=false;

var change = false;
var time = 0.0;
var annot = 0.0;
var chart;
var affectData = [["Time","Rating"]];
var playing = false;
var vid = document.getElementById("annot_target");
var video;
var dimension = window.sessionStorage.getItem("Dimension");
var data_ID=window.sessionStorage.getItem("data_id");
var conditions=["Linear", "Adaptive", "Generative", "None"];
var condition;
var overlay = false;
var video_id;

var video_history = [];

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

//Runs first time to set up overlays with dimension text
function load_page(){
    setup_overlays();
    annotation_setup();
}

//Setup
function annotation_setup() {
    reset_variables();

    setup_chart();

    raiseOverlay(conditions.length);
    condition = select_condition();
    console.log("Condition =" + condition);
    console.log("Dimension = " + dimension);

    let str = document.getElementById("annot_instructions").innerHTML;
    document.getElementById("annot_instructions").innerHTML=str.replaceAll("_dimension", dimension);

    console.log("Starting annotation");
    vid = document.getElementById("annot_target");
    
    video = load_video();
    vid.src=video.src;

    //!!!!!!!!Remove once we have videos, overrides video load from code
    //vid.src="Sample_1.mp4"; //!!!!!!!!!!!!Loads sample! Hard Coded! Remove when we have videos!

    vid.load();
}

function setup_overlays(){
    var clon = get_dimension_text();

    document.getElementById("annot_instructions").appendChild(clon);
   // document.getElementById("between").appendChild(clon);
    //document.getElementById("finished").appendChild(clon);
}

function get_dimension_text(){
    var temp = document.getElementById("valence_instructions");
    if(dimension=="valence"){
        temp = document.getElementById("valence_instructions");
    }
    else if (dimension=="arousal")
    {
        temp = document.getElementById("arousal_instructions");
    }
    else if (dimension=="tension"){
        temp = document.getElementById("tension_instructions");
    }
    else {
        console.log("Dimension coded wrong");
    }

    var clon = temp.content.cloneNode(true);
    return clon;
}

function setup_chart() {
    if(chart!=null){chart.destroy();}
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


function end_annotate(){
    playing=false;
    //First, export the annotation to the php file
    var name = `GalDef_Annot_${data_ID}`;
    export_csv(name);

    if(conditions.length>0){
        annotation_setup();
    }
    else{
        raiseOverlay(0);
    }
}

function raiseOverlay(remaining_conditions){
    if(remaining_conditions==4){
        document.getElementById("begin").style ="display:block";
    }
    else if (remaining_conditions>0){
        document.getElementById("between").style= "display:block";
    }
    else{
        console.log("Annotations finished!");
        document.getElementById("finished").style="display:block";
    }
}

function lower_overlay(){
    document.getElementById("begin").style ="display:none";
    document.getElementById("between").style= "display:none";
    document.getElementById("finished").style="display:none";
}

function build_csv(){
    //Encode header data
    var csv = "data_ID, Condition, Dimension, Video_ID\r\n";
    var data_ID = window.sessionStorage.getItem("data_id");
    var row = `${data_ID}, ${condition}, ${dimension}, ${video_id}\r\n`;
    csv+=row;

    //Data (has header for specific data variables)
    affectData.forEach(function(row){
        csv+=row.join(',');
        csv+="\r\n";
    });

    return csv;
}

const export_csv = (fileName) => {
    var csv=build_csv();

    if(save){
    let hiddenElement = document.createElement('a');
    hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);
    hiddenElement.target = '_blank';
    hiddenElement.download = fileName + '.csv';
    hiddenElement.click();
    }
    if(post_online){
        post_CSV(csv);
    }
}

function post_CSV (csv) {
    console.log("Posting CSV");

    // (A) CREATE BLOB OBJECT
    var myBlob = new Blob([csv], {type: "text/csv"});
  
    // (B) FORM DATA
    var data = new FormData();
    data.append("upfile", myBlob);

    // (C) AJAX UPLOAD TO SERVER
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "upload_annot.php");
    xhr.onload = function () {
      console.log(this.status);
      console.log(this.response);
    };
    xhr.send(data);
  }

//Load video and set video_id
function load_video() {
    var whichVideo = Math.floor(Math.random()*5);
    console.log(`WhichVideo = ${whichVideo}, Condition=${condition}`);
    var _video;
    if (condition == "Linear") {
        _video = linear_videos[whichVideo];
    }
    else if (condition == "Adaptive") {
        _video = adaptive_videos[whichVideo];
    }
    else if (condition == "Generative"){
        _video = generative_videos[whichVideo];
    }
    else if (condition=="None"){
        _video = none_videos[whichVideo];
    }
    console.log(_video);
    video_id=_video.id;
    video_history.push(video_id);
    console.log("Added " + video_id +" to history");
    return _video;
}

function reset_variables(){
    time=0.0;
    annot=0.0
    affectData=[["Timestamp", "Rating"]];
    playing = false;
    change=false;
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
    //console.log("Time:" + time + ", annot: "+annot);
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
        else if (e.code=="Backquote"){
            end_annotate();
        }

        annot += toChange;
        //console.log(dimension);
    }
}

function toQuestionnaire(){
window.sessionStorage.setItem("Video_history", JSON.stringify(video_history));
//console.log("Video history set :" + video_history);
window.location.href ="questionnaire.html";
}

function capitalizeFirstLetter(string){return string.charAt(0).toUpperCase() + string.slice(1);}