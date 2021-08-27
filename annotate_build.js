var StudentID;
var data_id;
var consent = false;
var dimension = "";

var consentDiv, demo_info, phase1_instructions, phase2_instructions;

function study_setup(){
    data_id='_'+Math.random().toString(36).substr(2, 9);
    consentDiv =document.getElementById("consentDiv");
    demo_info = document.getElementById("Demographic_information");
    phase1_instructions=document.getElementById("Phase1_Instructions");
    phase2_instructions=document.getElementById("Phase2_Instructions");
    
    var which_dimension=Math.floor(Math.random()*3);
    var temp = document.getElementById("valence_instructions");
    if(which_dimension==0){
        dimension = "valence";
        temp = document.getElementById("valence_instructions");
    }
    else if (which_dimension==1)
    {
        dimension = "arousal";
        temp = document.getElementById("arousal_instructions");
    }
    else if (which_dimension==2){
        dimension = "tension";
        temp = document.getElementById("tension_instructions");
    }
    else {
        console.log("Dimension coded wrong");
    }
    var str = document.getElementById("phase2_text").innerHTML;
    document.getElementById("phase2_text").innerHTML=str.replaceAll("_dimension", dimension);

    var clon = temp.content.cloneNode(true);
    phase2_instructions.appendChild(clon);
    
    temp = document.getElementById("annotation_instructions");
    clon = temp.content.cloneNode(true);
    str = clon.getElementById("annot_instr").innerHTML;
    clon.getElementById("annot_instr").innerHTML=str.replaceAll("_dimension", dimension);
    phase2_instructions.appendChild(clon);
}

function phase2(){
    phase2_instructions.style.display="block";
    phase2_instructions.scrollIntoView(true);
}

function submit_consent(){
    if(document.getElementById("consent").checked==true){
        consent=true;
        window.location.href="annotate.html";
    }
}

function scrollFromConsent(){
    if(document.getElementById("studentID").value.length>0){
    if(document.getElementById("consent").checked==true){
        consent=true;
        StudentID=document.getElementById("studentID").value;
        Consent_to_Instructions();
        document.getElementById("Phase1_Instructions").scrollIntoView(true);
    }
    else{
        window.alert("Please accept consent information (This may not be your fault, this is supposed to be impossible. Try re-loading the page)");
    }
}
else{
    document.getElementById("consent").checked=false;
    window.alert("Please enter your student ID");
}
}

// function open_GalDef(){
//     window.open("https://caleplut.itch.io/galacticdefense");
// }

function Consent_to_Instructions() {
    phase1_instructions.style.display="block";
}

function Load_annotation(){
save_data();
window.location.href ="annotate.html";
}

function save_data(){
window.sessionStorage.setItem("StudentID", StudentID);
window.sessionStorage.setItem("data_id", data_id);
window.sessionStorage.setItem("Consent", consent);
window.sessionStorage.setItem("Dimension", dimension);
}