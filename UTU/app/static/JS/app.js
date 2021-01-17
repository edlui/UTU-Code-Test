$('#datepicker').children().first().attr('selected', 'selected');

// when datapicker on change
$('#datepicker').on('change', function () {
    var selected = { "selected_date" : $(this).val() };
    if (selected.selected_date != 'empty') {
        $.ajax({
            type:'POST',
            url: "/datepicker", 
            dataType: 'json', 
            data: JSON.stringify(selected), 
            contentType: 'application/json;charset=UTF-8', 
            success: function(data){
                // empty the table body
                $('#tbody').empty();
                console.log(data);
                // need to +1 for the header
                for (var i = 0; i < Object.keys(data).length+1; i++){
                    // skip undefined row
                    if (data["currency"][i] != undefined){
                        // append the tbody
                        $('#tbody').append(
                        `<tr>
                        <th scope="row">`+ data["index"][i] +`</th>
                        <td>`+ data["currency"][i] +`</td>
                        <td>`+ data["price"][i] +`</td> 
                        <td class='`+ data["24h color"][i] +`'>`+ data["24h"][i] +`</td>
                        <td class='`+ data["7d color"][i] +`'>`+ data["7d"][i] +`</td>
                        <td class='`+ data["30d color"][i] +`'>`+ data["30d"][i] +`</td>
                        <td>`+ data["24h Volume"][i] +`</td>
                        <td>`+ data["Mkt Cap"][i] +`</td>
                        </tr>`
                        );
                    }
                }
            }
        });
    }
});