function search_by_keywords(){
    var server_endpoint = '/perform_search';

    $.ajax({headers : {},
        type: "POST",
        data: {
            "query" : $('#beerSearchInput').val()
        },
        dataType: "json",
        url: server_endpoint,
        success: function (data) {
            if (data.status_code === 200) {

                $('#searchTable tbody').html(
                    $.map(data.results, function (item, index) {
                        return '<tr> <td>'+ item.name[0] + '</td> <td>' + item.category[0] + '</td> <td>' + item.style[0] + '</td> <td>' + item.abv[0] + '</td> <td>' + item.ibu[0] + '</td> <td>' + item.brewery[0] + '</td> </tr>';
                    }).join());

            }
            else {
                alert("Unknown Error - Search Not Successful Due To Unforeseen Error.");
            }
    }});
}