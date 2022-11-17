$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_name").val(res.name);
        $("#promotion_description").val(res.description);
        $("#promotion_type").val(res.type);
        $("#promotion_value").val(res.promotion_value);
        $("#promotion_percent").val(res.promotion_percent);
        $("#promotion_status").val(res.status);
        if (res.status == true) {
            $("#promotion_available").val("true");
        } else {
            $("#promotion_available").val("false");
        }
        $("#promotion_expiry").val(res.expiry);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_name").val("");
        $("#promotion_description").val("");
        $("#promotion_type").val("");
        $("#promotion_value").val("");
        $("#promotion_percent").val("");
        $("#promotion_status").val("");
        $("#promotion_expiry").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Promotion
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#promotion_name").val();
        let description = $("#promotion_description").val();
        let type = $("#promotion_type").val();
        let value = $("#promotion_value").val();
        let percent = $("#promotion_percent").val();
        let status = $("#promotion_status").val() == "true";
        let expiry = $("#promotion_expiry").val();

        let data = {
            "name": name,
            "description": description,
            "type": type,
            "promotion_value": value,
            "promotion_percent": percent,
            "status": status,
            "expiry": expiry
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Promotion
    // ****************************************

    $("#update-btn").click(function () {

        let promotion_id = $("#promotion_id").val();
        let name = $("#promotion_name").val();
        let description = $("#promotion_description").val();
        let type = $("#promotion_type").val();
        let value = $("#promotion_value").val();
        let percent = $("#promotion_percent").val();
        let status = $("#promotion_status").val() == "true";
        let expiry = $("#promotion_expiry").val();

        let data = {
            "name": name,
            "description": description,
            "type": type,
            "promotion_value": value,
            "promotion_percent": percent,
            "status": status,
            "expiry": expiry
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/promotions/${promotion_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Promotion
    // ****************************************

    $("#retrieve-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Promotion
    // ****************************************

    $("#delete-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Promotion has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Promotion
    // ****************************************

    $("#search-btn").click(function () {
        let status = $("#promotion_status").val() == "true";

        let queryString = ""

        if (status) {
            queryString += 'status=' + status
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Description</th>'
            table += '<th class="col-md-2">Type</th>'
            table += '<th class="col-md-2">Value</th>'
            table += '<th class="col-md-2">Percent</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '<th class="col-md-2">Expiry</th>'
            table += '</tr></thead><tbody>'
            let firstPromotion = "";
            for(let i = 0; i < res.length; i++) {
                let promotion = res[i];
                table +=  `<tr id="row_${i}"><td>${promotion.id}</td><td>${promotion.name}</td><td>${promotion.description}</td><td>${promotion.type}</td><td>${promotion.promotion_value}</td><td>${promotion.promotion_percent}</td><td>${promotion.status}</td><td>${promotion.expiry}</td></tr>`;
                if (i == 0) {
                    firstPromotion = promotion;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPromotion != "") {
                update_form_data(firstPromotion)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
