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

$(document).ready(function () {
	// Add to cart
	$(".add_to_cart").on("click", function (e) {
		e.preventDefault();
		food_id = $(this).attr("data-id");
		url = $(this).attr("data-url");
		$.ajax({
			type: "GET",
			url: url,
			success: function (response) {
				if (response.status == "LOGIN_REQUIRED") {
					swal(response.message, "", "info").then(function () {
						window.location = "/tomato/login";
					});
				} else if (response.status == "Failed") {
					swal(response.message, "", "error");
				} else {
					let cart_counter = response.cart_counter.cart_count;
					$("#cart_counter").html(cart_counter);
					$("#qty-" + food_id).html(response.qty);

					//subtotal tax and grand total
					applyCartAmount(
						response.cart_amount.sub_total,
						response.cart_amount.tax,
						response.cart_amount.grand_total
					);
				}
			},
		});
	});

	// Decrease cart
	$(".remove_from_cart").on("click", function (e) {
		e.preventDefault();
		let food_id = $(this).attr("data-id");
		let url = $(this).attr("data-url");
		let cart_id = $(this).attr("data-cart");
		$.ajax({
			type: "GET",
			url: url,
			success: function (response) {
				console.log(response);
				if (response.status == "Failed") {
					swal(response.message, "", "error");
				} else {
					let cart_counter = response.cart_counter.cart_count;
					$("#cart_counter").html(cart_counter);
					swal(response.status, response.message, "success");
					$("#cart_counter").html(cart_counter);
					$("#qty-" + food_id).html(response.qty);
					applyCartAmount(
						response.cart_amount.sub_total,
						response.cart_amount.tax,
						response.cart_amount.grand_total
					);
					if (response.qty == 0) {
						checkCartCounter();
						removeCartItem(0, cart_id);
					}
				}
			},
		});
	});

	$(".item_qty").each(function () {
		let food_id = $(this).attr("id");
		let quantity = $(this).attr("data-qty");
		$("#" + food_id).html(quantity);
	});

	// Delete cCartitem
	$(".delete_cart").on("click", function (e) {
		e.preventDefault();
		cart_id = $(this).attr("data-id");
		url = $(this).attr("data-url");
		$.ajax({
			type: "GET",
			url: url,
			success: function (response) {
				if (response.status == "Failed") {
					swal(response.message, "", "error");
				} else {
					let cart_counter = response.cart_counter.cart_count;
					$("#cart_counter").html(cart_counter);
					$("#qty-" + cart_id).html(response.qty);
					swal(response.status, response.message, "success");
					applyCartAmount(
						response.cart_amount.sub_total,
						response.cart_amount.tax,
						response.cart_amount.grand_total
					);
					if (window.location.pathname == "/tomato/cart/") {
						removeCartItem(0, cart_id);
						checkCartCounter();
					}
				}
			},
		});
	});

	// delete cart element if quantiy is zero

	function removeCartItem(cartItemQuantity, CartId) {
		if (cartItemQuantity <= 0) {
			let cart_item = document.getElementById("cart-item-" + CartId);

			if (cart_item) {
				cart_item.remove();
			}
		}
	}

	//Check if teh cart is empty
	const checkCartCounter = function () {
		let cart_counter = document.getElementById("cart_counter").innerHTML;

		if (cart_counter == 0) {
			let emptyCart = document.getElementById("empty-cart");
			if (emptyCart) {
				emptyCart.classList.remove("d-none");
			}
		}
	};

	// apply cart amounts
	const applyCartAmount = function (subTotal, tax, grandTotal) {
		console.log(subTotal);
		console.log(tax);
		console.log(grandTotal);

		if (window.location.pathname == "/tomato/cart/") {
			$("#subtotal").html(subTotal);
			$("#tax").html(tax);
			$("#total").html(grandTotal);
		}
	};
});
