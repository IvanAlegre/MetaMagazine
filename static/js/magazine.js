var hideNew = function(idMsg){
    document.getElementById('new'+idMsg).innerHTML = '';    
}

var showNew = function(idMsg){
    // Make the call to retrieve new
    res = new XMLHttpRequest();
    res.onreadystatechange = function(){
        if (res.readyState==4 && res.status==200){
            document.getElementById('new'+idMsg).innerHTML = res.responseText;
        }
    }
    
    res.open("GET","/api/news/"+idMsg, true);
    res.send();
}

var getXML = function(){
    return new XMLHttpRequest();
}

var showAll = function(className){
    // Retrieve all the objects with class new
    elems = document.getElementsByClassName(className)
    
    for (var i=0; i<elems.length; i++){
        // Get the id of the msg
        idMsg = elems[i]['id'].replace('new','')

        var res = getXML();
        res.open("GET","/api/news/"+idMsg, false);
        res.send();    
        document.getElementById('new'+idMsg).innerHTML = res.responseText; 
    }
}

var hideAll = function(){
    // Retrieve all the objects with class new
    elems = document.getElementsByClassName(className)
    
    for (var i=0; i<elems.length; i++){
        document.getElementById('new'+idMsg).innerHTML = '';         
    }
}