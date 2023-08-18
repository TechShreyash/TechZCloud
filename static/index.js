const form = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const urlInput = document.getElementById("url-input");
const progressBar = document.getElementById("progressor");
const vfile = document.getElementById("vfile");
const vtime = document.getElementById("vtime");
const vprog = document.getElementById("vprog");
const vspeed = document.getElementById("vspeed");
const udiv1 = document.getElementById("udiv-main");
const udiv2 = document.getElementById("udiv2-main");
const hstatus = document.getElementById("hstatus");

function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return "0 Bytes";

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB"];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

function formatTime(sec_num) {
    const hours = Math.floor(sec_num / 3600);
    const minutes = Math.floor((sec_num - hours * 3600) / 60);
    const seconds = Math.floor(sec_num - hours * 3600 - minutes * 60);

    let text = "";
    if (hours > 0) {
        text += hours + "hour ";
        if (minutes > 0) {
            text += minutes + "min ";
        }
    } else if (minutes > 0) {
        text += minutes + "min ";
        if (seconds > 0) {
            text += seconds + "sec";
        }
    } else {
        text += seconds + "sec";
    }
    return text;
}

function FileUploader(file) {
    udiv1.style.display = "none";
    udiv2.style.display = "flex";
    vfile.innerHTML = file.name;
    vtime.innerHTML = "Calculating...";
    vprog.innerHTML = "0%";
    vspeed.innerHTML = "Calculating...";

    let done = 0;
    let time = new Date().getTime();
    let speed = 0;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("Connection", "keep-alive");
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload", true);
    xhr.send(formData);

    xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
            const ctime = new Date().getTime();
            if (ctime - time > 1000) {
                time = ctime;
                speed = e.loaded - done;
                tRemaining = formatTime((e.total - e.loaded) / speed);
                speed = formatBytes(speed).toString() + "/s";

                const percentComplete = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = `${percentComplete}%`;
                vprog.innerHTML =
                    formatBytes(e.loaded) +
                    "/" +
                    formatBytes(e.total) +
                    " | " +
                    percentComplete +
                    "%";
                vtime.innerHTML = tRemaining;
                vspeed.innerHTML = speed;

                done = e.loaded;
            }
        }
    };

    xhr.onerror = (e) => {
        alert("Error! Upload failed. Can't connect to server.");
        udiv1.style.display = "flex";
        udiv2.style.display = "none";
        return;
    };

    xhr.onreadystatechange = function () {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            const fileHash = xhr.responseText;
            TgFileUploader(fileHash);
        }
    };
}

function TgFileUploader(fileHash) {
    hstatus.innerHTML = "Processing...";
    udiv1.style.display = "none";
    udiv2.style.display = "flex";

    let isProc = true;
    done = 1;
    let speed;

    function updateProcess() {
        if (isProc) {
            const xmlHttp = new XMLHttpRequest();
            xmlHttp.open("GET", "/process/" + fileHash, true);
            xmlHttp.send(null);

            xmlHttp.onreadystatechange = function () {
                if (xmlHttp.readyState == XMLHttpRequest.DONE) {
                    let data = xmlHttp.responseText;
                    data = JSON.parse(data);

                    if (data["message"]) {
                        isProc = false;
                        window.location = "/file/" + fileHash;
                    }
                    const current = data["current"];
                    const total = data["total"];

                    speed = (current - done) / 5;
                    tRemaining = formatTime((total - current) / speed);
                    speed = formatBytes(speed).toString() + "/s";

                    const percentComplete = Math.round((current / total) * 100);
                    progressBar.style.width = `${percentComplete}%`;
                    vprog.innerHTML =
                        formatBytes(current) +
                        "/" +
                        formatBytes(total) +
                        " | " +
                        percentComplete +
                        "%";
                    vtime.innerHTML = tRemaining;
                    vspeed.innerHTML = speed;

                    done = current;
                }
                if (xmlHttp.readyState == 4 && xmlHttp.status == 400) {
                    isProc = false;
                    alert("Error! Upload failed. Can't connect to server.");
                    udiv1.style.display = "flex";
                    udiv2.style.display = "none";
                    return;
                }
            };
        } else {
            return;
        }
        setTimeout(updateProcess, 5000);
    }
    setTimeout(updateProcess, 5000);
}

function RemoteUploader(url) {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/remote_upload", true);
    xhr.setRequestHeader("url", url);
    xhr.send(null);

    xhr.onreadystatechange = function () {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            hstatus.innerHTML = "Uploading...";
            // downloading file from remote to server
            const fileHash = xhr.responseText;
            vfile.innerHTML = fileHash + ".temp";
            udiv1.style.display = "none";
            udiv2.style.display = "flex";

            let isProc = true;
            done = 1;

            function updateProcess() {
                if (isProc) {
                    const xmlHttp = new XMLHttpRequest();
                    xmlHttp.open("GET", "/remote_status/" + fileHash, true);
                    xmlHttp.send(null);
                    xmlHttp.onreadystatechange = function () {
                        if (xmlHttp.readyState == XMLHttpRequest.DONE) {
                            let data = xmlHttp.responseText;
                            data = JSON.parse(data);

                            if (data["message"] == "complete") {
                                isProc = false;
                                TgFileUploader(fileHash);
                                return;
                            }
                            if (data["message"]) {
                                isProc = false;
                                alert(data["message"]);
                                udiv1.style.display = "flex";
                                udiv2.style.display = "none";
                                return;
                            }
                            const current = data["current"];
                            const total = data["total"];

                            speed = (current - done) / 5;
                            tRemaining = formatTime((total - current) / speed);
                            speed = formatBytes(speed).toString() + "/s";

                            const percentComplete = Math.round((current / total) * 100);
                            progressBar.style.width = `${percentComplete}%`;
                            vprog.innerHTML =
                                formatBytes(current) +
                                "/" +
                                formatBytes(total) +
                                " | " +
                                percentComplete +
                                "%";
                            vtime.innerHTML = tRemaining;
                            vspeed.innerHTML = speed;

                            done = current;
                        }
                        if (xmlHttp.readyState == 4 && xmlHttp.status == 400) {
                            isProc = false;
                            alert("Error! Upload failed. Can't connect to server.");
                            udiv1.style.display = "flex";
                            udiv2.style.display = "none";
                            return;
                        }
                    };
                } else {
                    return;
                }
                setTimeout(updateProcess, 5000);
            }

            setTimeout(updateProcess, 5000);
        }
    };
}

// submit button handler

form.addEventListener("submit", (e) => {
    try {
        e.preventDefault();

        const file = fileInput.files[0];
        let url = urlInput.value;
        if (file) {
            if (file.size < 9.8 * 1024 * 1024) {
                alert("File size must be more than 10MB");
                return;
            }
            if (file.size > 1.98 * 1024 * 1024 * 1024) {
                alert("File size must be less than 2GB");
                return;
            }

            FileUploader(file);
        } else if (url) {
            if (url.trim() != "") {
                console.log(url);
                url = url.trim();

                RemoteUploader(url);
            }
        } else {
            alert("Select a File or enter a URL");
            return;
        }
    } catch (err) {
        alert(err);
        udiv1.style.display = "flex";
        udiv2.style.display = "none";
        return;
    }
});
