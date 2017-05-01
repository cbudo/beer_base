function beer_or_brewery(){
    entity = $('#entity-chooser').val();
    console.log(entity);
    if(entity === 'beer') {
        $('#brewery_sel').show();
        $('#ibu_sel').show();
        $('#abv_sel').show();
        $('#location_sel').hide();
    }
    else{
        $('#brewery_sel').hide();
        $('#ibu_sel').hide();
        $('#abv_sel').hide();
        $('#location_sel').show();
    }
}

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
                        return '<tr> <td>'+ cat_name(item.name) + '</td> <td>' + cat_name(item.category) + '</td> <td>'
                        + cat_name(item.style) + '</td> <td>' + item.abv[0] + '</td> <td>' + item.ibu[0] + '</td> <td>'
                        + cat_name(item.brewery) + '</td> </tr>';
                    }).join());

            }
            else {
                alert("Unknown Error - Search Not Successful Due To Unforeseen Error.");
            }
    }});
}

function cat_name(array_of_words){
    full_string = ""
    array_of_words.forEach(function(word){
        if(full_string === ""){
            full_string += word;
        }
        else{
            full_string += " " + word;
        }
    });
    return full_string;
}