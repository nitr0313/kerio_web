function copyFromCurrentIP(id){
    var textToCopy = document.getElementById("current_ip").textContent;
    var whereToCopy = document.getElementById("id_ipaddress");
    whereToCopy.value = textToCopy;
}