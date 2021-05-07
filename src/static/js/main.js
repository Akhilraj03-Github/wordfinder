var selectedTag = '';

function init(){
    $('#labelId1').hide();
    $('#clusterDiv1').hide();
}

// find all indexes of selected word(substr) in sentence(str)
function searchSubStr(str,subStr){
    var positions = new Array();
    var pos = str.indexOf(subStr);
    while(pos>-1){
        positions.push(pos);
        pos = str.indexOf(subStr,pos+1);
    }
    return positions;
}

function findByTag(selWord, tag, rowResult, wordResultKWIC){
  /*
    selWord: selected word
    rowResult: sentences
    tag: POS

  */
    $("#tagInput1").attr("value",tag);
    var ulControl = $('#sentencesGroup');
    ulControl.find("li").remove();
    if(wordResultKWIC.length > 0){
        $('#labelId1').show();
        $('#clusterDiv1').show();
    }

    outstr = '<pre>'
    for(i=1; i<wordResultKWIC.length+1; i++){
         outstr += "<li class=\"list-group-item d-flex justify-content-between align-items-center\">" +
           wordResultKWIC[i-1] +
           "<span class=\"badge badge-primary badge-pill\">"+ i + "</span>" +
          "</li>"
        //outstr += '<br />'
    }

    outstr += '</pre>'
    ulControl.append(outstr);
}








