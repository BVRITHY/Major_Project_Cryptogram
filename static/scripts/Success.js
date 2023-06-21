let input = document.querySelector("#upload-form");
let clearButton = document.querySelector(".clear-button");
let downloadButton = document.querySelector(".download-button");
let uploadButton = document.querySelector(".input-files");

input.addEventListener("change", stateHandle, {once : true});

function stateHandle() {
    document.querySelector(".input-files").style.backgroundColor = '#9A3334';
    document.querySelector("#fa-fa-upload").className = 'fa fa-check';
    clearButton.disabled = false;
    downloadButton.disabled = false;
    uploadButton.disabled = true;
}


function Submit(){
    document.getElementById("upload-form").submit();
    stateHandle();
}
