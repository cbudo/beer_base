function search_by_keywords(){
    var server_endpoint = '/perform_search';

    $.ajax({headers : {},
        type: "POST",
        data: {
            "query" : $('#beerSearchInput').val(),
            "filter" : $('#filter-chooser').val(),
            "entity": $('#entity-chooser').val()
        },
        dataType: "json",
        url: server_endpoint,
        success: function (data) {
            if (data.status_code === 200) {

                $('#searchTable tbody').html(
                    $.map(data.results, function (item, index) {
                        return '<tr> <td>'+ return_full_string(item.name) + '</td> <td>' + return_full_string(item.category) + '</td> <td>' + return_full_string(item.style) + '</td> <td>' + item.abv[0] + '</td> <td>' + item.ibu[0] + '</td> <td>' + return_full_string(item.brewery) + '</td> </tr>';
                    }).join());

            }
            else {
                alert("Unknown Error - Search Not Successful Due To Unforeseen Error.");
            }
    }});
}

function return_full_string(array_of_words){
    full_string = ""
    array_of_words.forEach(function(word){
        if(full_string == ""){
            full_string += word;
        }
        else{
            full_string += " " + word;
        }
    });
    return full_string;
}