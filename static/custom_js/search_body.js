function beer_or_brewery(){
    entity = $('#entity-chooser').val();
    if(entity === 'beer') {
        $('#brewery_sel').show();
        $('#style_sel').show();
        $('#category_sel').show();
        $('#city_sel').hide();
        $('#state_sel').hide();
        $('#country_sel').hide();
        $('#beerTable').show();
        $('#breweryTable').hide();
    }
    else{
        $('#brewery_sel').hide();
        $('#style_sel').hide();
        $('#category_sel').hide();
        $('#city_sel').show();
        $('#state_sel').show();
        $('#country_sel').show();
        $('#beerTable').hide();
        $('#breweryTable').show();
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
                if (entity === 'beer'){
                    $('#beerTable tbody').html(
                        $.map(data.results, function (item, index) {
                            return '<tr> <td>'+ cat_name(item.name) + '</td> <td>' + cat_name(item.category) + '</td> <td>'
                            + cat_name(item.style) + '</td> <td>' + item.abv[0] + '</td> <td>' + item.ibu[0] + '</td> <td>'
                            + cat_name(item.brewery) + '</td> </tr>';
                        }).join());
                }
                else {
                    $('#breweryTable tbody').html(
                        $.map(data.results, function (item, index) {
                            return '<tr> <td>'+ cat_name(item.name) + '</td> <td>' + cat_name(item.city) + '</td> <td>'
                            + cat_name(item.state) + '</td> <td>' + cat_name(item.country) + '</td> </tr>';
                        }).join());
                }
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