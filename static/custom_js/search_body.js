var table_contents = [];

function beer_or_brewery(){
    entity = $('#entity-chooser').val();
    if(entity === 'beer') {
        $('#brewery_sel').show();
        $('#style_sel').show();
        $('#category_sel').show();
        $('#city_sel').hide();
        $('#state_sel').hide();
        $('#country_sel').hide();
        $('#beer-row').show();
        $('#brewery-row').hide();
        $('#brewery-table').find('tbody').html("")
    }
    else{
        $('#brewery_sel').hide();
        $('#style_sel').hide();
        $('#category_sel').hide();
        $('#city_sel').show();
        $('#state_sel').show();
        $('#country_sel').show();
        $('#beer-row').hide();
        $('#brewery-row').show();
        $('#beer-table').find('tbody').html("")
    }
}

function search_by_keywords(){
    var server_endpoint = '/perform_search';

    var query = $('#beerSearchInput').val();
    var filter = $('#filter-chooser').val();
    var entity = $('#entity-chooser').val();
    if(!entity || entity === ''){
        entity = 'beer';
    }
    if(!filter){
        filter = '';
    }
    if(!query){
        query = '';
    }
    $.ajax({headers : {},
        type: "POST",
        data: {
            "query" : query,
            "filter" : filter,
            "entity": entity
        },
        dataType: "json",
        url: server_endpoint,
        success: function (data) {
            table_contents = data.results;
            if (entity === 'beer') {
                $('#beer-table').find('tbody').html(
                    $.map(data.results, function (item, index) {
                        return '<tr> <td> <a href="/beer/' + item.beer_id[0] + '">' + cat_name(item.name) +
                            '</a> </td> <td>' + cat_name(item.category) + '</td> <td>' + cat_name(item.style) +
                            '</td> <td>' + item.abv[0] + '</td> <td>' + item.ibu[0] + '</td> <td>'
                            + cat_name(item.brewery) + '</td> <td>' + '<button onclick="like_beer(' + item.beer_id[0] + ')">Like</button>' + '</td> </tr>';
                    }).join());
            }
            else {
                $('#brewery-table').find('tbody').html(
                    $.map(data.results, function (item, index) {
                        return '<tr> <td> <a href="/brewery/' + item.brewery_id[0] + '">' + cat_name(item.name)
                            + '</a> </td> <td>' + cat_name(item.city) + '</td> <td>' + cat_name(item.state) +
                            '</td> <td>' + cat_name(item.country) + '</td> </tr>';
                    }).join());
            }
        },
        failure: function (data) {
            alert("Unknown Error - Search Not Successful Due To Unforeseen Error.");
    }});
}

function like_beer(beer_id){

    var server_endpoint = '/like_beer';

    var username = retrieve_username();

    $.ajax({headers : {},
        type: "POST",
        data: {
            "username" : username,
            "beer_id": beer_id
        },
        dataType: "json",
        url: server_endpoint,
        success: function (data) {
            if(data.liked === 'no'){
                alert('Beer Already Liked Before!');
            }
            else {
                alert("Beer Liked!");
            }
            return true;
        },
        error: function (data) {
            alert("Query for existing user failed - could not log in.");
            return false;
        }
    });
}

function cat_name(array_of_words){
    var full_string = "";
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