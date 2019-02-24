$(function () {
	$("li:not(:has(ul))").each(function (index) {
		$(this).addClass('last');
	});
	$('LI:has(ul) > SPAN').click(function (e) {
		$(this).parent().children('UL').toggle();
		$(this).parent().toggleClass("collapsed");
	});

	//$('LI:has(ul) > SPAN').click();
});
