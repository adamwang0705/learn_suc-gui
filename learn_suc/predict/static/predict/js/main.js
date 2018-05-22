// Shorthand for $( document ).ready()
$(function() {
    // Perform actions after the DOM is loaded and ready
    print_sys_time();

    $("#input_partial_item").autocomplete({
        source: "/learn_suc/index/search_item/",  // Subject to change
        select: function (event, ui) { //item selected
            auto_complete_select_handler(event, ui);
            return false;
        },
        minLength: 2,
        delay:200
    })
    .autocomplete("instance")._renderItem = function(ul, item) {
      return $( "<li>" )
        .append( "<div>(" + item.type_name + ") " + item.name + "</div>" )
        .appendTo( ul );
    };

});

function print_sys_time() {
    var datetime = new Date();
    $("footer").append("<p>" + datetime + "</p>")
}

function auto_complete_select_handler(event, ui) {
    var selected_item = ui.item;
    $("#input_partial_item").val(selected_item.name);
    $("#searched_item_id").val(selected_item.item_id);
}
