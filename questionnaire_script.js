var save = false; //MUST BE FALSE FOR LIVE
var post_online = true; //MUST BE TRUE FOR LIVE
var video_history = JSON.parse(window.sessionStorage.getItem("Video_history"));
var videos_exist = true;
var data_ID

const load_questionnaire = () => {
    populate_videos();
    populate_video_answer();
}

function submit_questionnaire() {
    var fileName = `GalDef_Question_${data_ID}`;
    export_q_csv(fileName);
}

function build_q_csv() {
    //Encode header data
    var csv = "data_ID, Codeword, StudentID, Consent, Age, Pronouns, Weekly_hours, Dimension\r\n";
    data_ID = window.sessionStorage.getItem("data_id");
    var codeword = window.sessionStorage.getItem("Codeword");
    var studentID = window.sessionStorage.getItem("StudentID");
    var consent = window.sessionStorage.getItem("Consent");
    var dimension = window.sessionStorage.getItem("Dimension");
    var age = document.getElementById("age").value;
    var pronouns = document.getElementById("pronouns").value;
    var weekly_hours = document.getElementById("hoursPerWeek").value;

    var row = `${data_ID}, ${codeword}, ${studentID}, ${consent}, ${age}, ${pronouns}, ${weekly_hours}, ${dimension} \r\n`;
    csv += row;

    csv += "Music_match, Music_emotion ,Immersion, Preference, Comments, Email, \r\n";
    var music_match = document.getElementById("music_match").value;
    var music_emotion = document.getElementById("music_emotion").value;
    var immersion = document.getElementById("immersion").value;
    var preference = document.getElementById("preference").value;
    var comments = document.getElementById("comments").value;
    var email = document.getElementById("email").value;
    row = `${music_match}, ${music_emotion}, ${immersion}, ${preference}, ${comments}, ${email}`;
    csv += row;

    return csv;
}

const export_q_csv = (fileName) => {
    var csv = build_q_csv();

    if (save) {
        let hiddenElement = document.createElement('a');
        hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);
        hiddenElement.target = '_blank';
        hiddenElement.download = fileName + '.csv';
        hiddenElement.click();
        document.getElementById("endQuest").style = "display:block";
        mTurkText();
    }
    if (post_online) {
        post_CSV(csv);
    }
}

function post_CSV(csv) {
    console.log("Posting CSV");

    // (A) CREATE BLOB OBJECT
    var myBlob = new Blob([csv], { type: "text/csv" });

    // (B) FORM DATA
    var data = new FormData();
    data.append("upfile", myBlob);

    // (C) AJAX UPLOAD TO SERVER
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "upload_quest.php");
    xhr.setRequestHeader("Cache-Control", "no-cache, no-store, max-age=0");
    xhr.onload = function () {
        console.log(this.status);
        console.log(this.response);
    };
    xhr.send(data);

    xhr.onreadystatechange = upload_state;

    function upload_state() {
        //console.log(xhr.readyState)
        if (xhr.readyState === XMLHttpRequest.DONE) {
            document.getElementById("endQuest").style = "display:block";
            mTurkText();
            //annotate_finish();
        }
    }
}

function mTurkText(){
    if (sessionStorage.getItem("mTurk") == "true") {
        text = document.getElementById("mTurkText");
        text.style.display = "block";
        var str = document.getElementById("mTurkText").innerHTML;
        document.getElementById("mTurkText").innerHTML = str.replaceAll("_id", data_ID);
    }
}

const populate_videos = () => {

    var vid1_src = find_video_source(video_history[0]);
    var vid2_src = find_video_source(video_history[1]);
    var vid3_src = find_video_source(video_history[2]);
    var vid4_src = find_video_source(video_history[3]);

    //console.log(`Srcs: ${vid1_src}, ${vid2_src}, ${vid3_src}, ${vid4_src}`);

    if (videos_exist) {
        document.getElementById("vid_1").src = vid1_src;
        document.getElementById("vid_2").src = vid2_src;
        document.getElementById("vid_3").src = vid3_src;
        document.getElementById("vid_4").src = vid4_src;
    }
}
const populate_video_answer = () => {
    var video_1 = video_history[0];
    var video_2 = video_history[1];
    var video_3 = video_history[2];
    var video_4 = video_history[3];
    document.getElementById("match_A").value = video_1;
    document.getElementById("match_B").value = video_2;
    document.getElementById("match_C").value = video_3;
    document.getElementById("match_D").value = video_4;

    document.getElementById("emotion_A").value = video_1;
    document.getElementById("emotion_B").value = video_2;
    document.getElementById("emotion_C").value = video_3;
    document.getElementById("emotion_D").value = video_4;


    document.getElementById("immersion_A").value = video_1;
    document.getElementById("immersion_B").value = video_2;
    document.getElementById("immersion_C").value = video_3;
    document.getElementById("immersion_D").value = video_4;

    document.getElementById("preference_A").value = video_1;
    document.getElementById("preference_B").value = video_2;
    document.getElementById("preference_C").value = video_3;
    document.getElementById("preference_D").value = video_4;
}

const find_video_source = (video_id) => {
    if (video_id.includes("Linear")) {
        for (_video of linear_videos) {
            if (_video.id == video_id) {
                return _video.src;
            }
        }
    }
    else if (video_id.includes("Adaptive")) {
        for (_video of adaptive_videos) {
            if (_video.id == video_id) {
                return _video.src;
            }
        }
    }
    else if (video_id.includes("Generative")) {
        for (_video of generative_videos) {
            if (_video.id == video_id) {
                return _video.src;
            }
        }
    }
    else if (video_id.includes("None")) {
        for (_video of none_videos) {
            if (_video.id == video_id) {
                return _video.src;
            }
        }
    }
    else { console.log("No condition in ID?") }
}