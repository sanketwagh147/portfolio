let autocomplete;

function initAutoComplete() {
	autocomplete = new google.maps.places.Autocomplete(
		document.getElementById("id_address"),
		{
			types: ["geocode", "establishment"],
			//default in this app is "IN" - add your country code
			componentRestrictions: { country: ["in"] },
		}
	);
	// function to specify what should happen when the prediction is clicked
	autocomplete.addListener("place_changed", onPlaceChanged);
}

function onPlaceChanged() {
	var place = autocomplete.getPlace();

	// User did not select the prediction. Reset the input field or alert()
	if (!place.geometry) {
		document.getElementById("id_address").placeholder = "Start typing...";
	} else {
		console.log("place name=>", place.name);
	}
	// get the address components and assign them to the fields
	// console.log(place);
	let geocoder = new google.maps.Geocoder();
	let address = document.getElementById("id_address").value;
	// console.log(address);

	geocoder.geocode({ address: address }, function (results, status) {
		// console.log("RESULTS->", results);
		// console.log("STATUS->", status);
		if (status == google.maps.GeocoderStatus.OK) {
			let latitude = results[0].geometry.location.lat();
			let longitude = results[0].geometry.location.lng();
			console.log(latitude, longitude);
			$("#id_latitude").val(latitude);
			$("#id_longitude").val(longitude);
			$("#id_address").val(address);
		}
	});

	// get other address data
	for (let i = 0; i < place.address_components.length; i++) {
		for (j = 0; j < place.address_components[i].types.length; j++) {
			data = place.address_components[i];
			if (data.types[j] == "country") {
				$("#id_country").val(data.long_name);
			}
			if (data.types[j] == "administrative_area_level_1") {
				$("#id_state").val(data.long_name);
			}
			if (data.types[j] == "locality") {
				$("#id_city").val(data.long_name);
			}
			// if no pincode found reset to blank
			if (data.types[j] == "postal_code") {
				$("#id_pin_code").val(data.long_name);
			} else {
				$("#id_pin_code").val("");
			}
		}
	}
}