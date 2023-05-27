
document.getElementById("typediv").display = "none";
document.getElementById("extdiv").display = "none";


document.getElementById("url").onchange = ()=>{
    document.getElementById("typediv").display = "block";
}


// function for showing extension
const loadExt = (event)=>{
    event.preventDefault()
    let fileType = document.getElementById("type").value;
    if (fileType=="video") {
        document.getElementById("extension").length = 0;
        document.getElementById("extdiv").display = "block";
        
        extensions = [
            "mp4",
            "webm",
            "3gpp"
        ]
        for (let key in extensions) {
            var ext = document.getElementById("extension")
            var opt = document.createElement("option");
            opt.value = extensions[key];
            opt.innerHTML = extensions[key];
            ext.append(opt)
        }
    } else if (fileType=="audio") {
        document.getElementById("extension").length = 0;
        document.getElementById("extdiv").display = "block";
        
        extensions = [
            "mp3",
            "wav"
        ]
        for (let key in extensions) {
            var ext = document.getElementById("extension")
            var opt = document.createElement("option");
            opt.value = extensions[key];
            opt.innerHTML = extensions[key];
            ext.append(opt)
        }
    }
}

// fetch function for showing extensions
const loadRes =  async (event) => {
    event.preventDefault()
    document.getElementById("download").disabled=true
    document.getElementById("resdiv").display = "none";
    document.getElementById("res").length = 0;
    // const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let formData = {
        url: document.querySelector('[name=url]').value,
        type: document.querySelector('[name=type]').value,
        ext: document.querySelector('[name=extension]').value
    }
    console.log(formData)

    const response = await fetch('/resolution/', {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(formData)
    })
    const jsonData = await response.json();
    console.log(jsonData)

    if (Object.keys(jsonData).length==0) {
        document.getElementById("urlVal").innerHTML = "Something wrong with url please check it again!"
    } else {
        document.getElementById("res").length = 0;
        document.getElementById("resdiv").display = "block";
        if (document.getElementById("type").value=="video"){
            document.getElementById("resLabel").innerHTML = "Resolution";
        } else {
            document.getElementById("resLabel").innerHTML = "Bitrate";
        }
        
        for (let key in jsonData) {
            var resType = document.getElementById("res")
            var opt = document.createElement("option");
            opt.value = jsonData[key];
            opt.innerHTML = jsonData[key];
            resType.append(opt)
        }
        document.getElementById("download").disabled=false
    }
}

document.getElementById("type").addEventListener("change", loadExt);
document.getElementById("type").addEventListener("change", loadRes);
