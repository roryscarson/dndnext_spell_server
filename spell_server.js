function go_to_spell() {
	location.href = 'http://localhost:8080/' + $("#spell_name_txt").val() + '/';
}
$("#get_spell_btn").click(function() {
	go_to_spell();
});
$("#spell_name_txt").keypress(function(event) {
    if (event.which == 13) {
        event.preventDefault();
        go_to_spell();
    }
});


