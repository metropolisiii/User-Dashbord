$(document).ready(function(){
	function upload(event) {
		event.preventDefault();
		var data = new FormData($('#upload_photo_form_form').get(0));
		
		$.ajax({
			url: $(this).attr('action'),
			type: $(this).attr('method'),
			data: data,
			dataType: 'json',
			cache: false,
			processData: false,
			contentType: false,
			success: function(data) {
				if (data.status == 'success'){
					location.reload();					
				}
				else
					$('#photo_upload_errors').html('There was an error uploading this image. Please make sure that this is a valid image.');
			}
		});
		return false;
	}
	$('#upload_photo_form_form').submit(upload);
	$('#update_info_form').submit(function(event){
		event.preventDefault();
		var data = new FormData($('#update_info_form').get(0));
		
		$.ajax({
			url: $(this).attr('action'),
			type: $(this).attr('method'),
			data: data,
			dataType: 'json',
			cache: false,
			processData: false,
			contentType: false,
			success: function(data) {
				if (data.status == 'success'){
					location.reload();					
				}
				else
					$('#update_info_errors').html('There was an error updating your information. Please make sure all information is valid');
			}
		});
		return false;
	});
	$('.x_panel, .sameheight').matchHeight();
	$('#user_photo').click(function(){
		$('#user_profile_options').toggle();
	});
});

/* Remove user profile popup if any part of the body is clicked */
$(document).mouseup(function (e)
{
    var container = $("#user_profile_options");

    if (!container.is(e.target) // if the target of the click isn't the container...
        && container.has(e.target).length === 0) // ... nor a descendant of the container
    {
        container.hide();
    }
});


function getSelectList(list, val){
	for (var i = 0, len = list.length; i < len; i++) {
	  if (list[i].name == val) {
		 return list[i].subcats;
	  }
	}
	return false;
}

