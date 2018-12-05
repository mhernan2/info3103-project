var app=new Vue({
	el: '#app',
	data: {
		login: false,
		gifts: [],
		user_id: '',
		user_name: '',
		users: [],
		giftlist_title: 'Gifts Received'
	},

	created: function () {
		this.check_login();
		this.get_users();
	},

	methods:{
		check_login: function() {
			let app = this;
			axios.get('http://info3103.cs.unb.ca:36371/login')
			.then(function (response) {
				app.login = true;
				app.user_id = response.data.user.user_id;
				app.user_name = response.data.user.first_name + ' ' + response.data.user.last_name;
			})
			.catch(function(error) {
				console.log('user not logged in');
				app.login = false;
			});
		},
		login_user: function() {
			let data = {
				username: $('#login-input').val(),
				password: $('#pw-input').val()
			}

			axios.post('http://info3103.cs.unb.ca:36371/login', data)
			.then(function (response) {
				if (response.data['status'] == 'success') {
					app.login = true;
					$('#login-form').addClass('d-none');
					app.user_id = data.username;
				}
			})
			.catch(function(error) {
				$('#login-input + .invalid-feedback').show();
				$('#pw-input + .invalid-feedback').show();
			});
		},
		logout_user: function() {
			axios.delete('http://info3103.cs.unb.ca:36371/login')
			.then(function (response) {
				app.login = false;
				app.gifts = [];
				app.user_id = '';
			});
		},
		show_register_form: function() {
			this.clear_elements();
			$('#register-form').removeClass('d-none');
		},
		register_user: function() {
			let register_form = $('#register-form');
			let first_name = register_form.find('#firstname-input').val();
			let last_name = register_form.find('#lastname-input').val();
			let username = register_form.find('#login-input-2').val();
			let password = register_form.find('#pw-input-2').val();

			let data = {
				first_name: first_name,
				last_name: last_name,
				username: username,
				password: password
			}

			axios.post('http://info3103.cs.unb.ca:36371/users', data)
			.then(function (response) {
				if (response.data['status'] == 'success') {
					app.login = true;
					$('#login-form').addClass('d-none');
				}
			})
			.catch(function(error) {
				$('#login-input-2 + .invalid-feedback').show();
				$('#pw-input-2 + .invalid-feedback').show();
			});
		},
		show_gifts: function(sent, user_id='') {
			// check if user is logged in
			let app = this;
			user_id = !user_id ? app.user_id : user_id;
			if (this.login) {
				q = sent ? '?sent=true' : '';
				axios.get('http://info3103.cs.unb.ca:36371/users/' + user_id + '/gifts' + q)
				.then(function (response) {
					app.gifts = response.data.gifts;
					app.clear_elements();
					$('#gift-list').removeClass('d-none');
				})
				.catch(function(error) {
					console.log('an error occurred');
				});
			}
		},
		show_gifts_sent: function(user_id, name) {
			let app = this;
			app.giftlist_title = 'Gifts Sent by ' + name;
			app.show_gifts(true, user_id);
		},
		show_gifts_received: function(user_id, name) {
			let app = this;
			app.giftlist_title = 'Gifts Received by ' + name;
			app.show_gifts(false, user_id);
		},
		show_wishlist: function(user='', object=false) {
			let app = this;
			let user_id = object ? user.user_id : user;
			if (!user_id) {
				app.giftlist_title = 'Overall Wishlist';
			} else if (app.user_id == user_id) {
				app.giftlist_title =  'My Wishlist';
			} else {
				app.giftlist_title = `${user.first_name} ${user.last_name}'s Wishlist`;
			}
			
			if (this.login) {
				q = user_id ? `?user_id=${user_id}`: '';
				axios.get('http://info3103.cs.unb.ca:36371/wishlist' + q)
				.then(function (response) {
					app.gifts = response.data.wishlist;
					app.clear_elements();
					$('#gift-list').removeClass('d-none');
				})
				.catch(function(error) {
					console.log('an error occurred');
				});
			}
		},
		show_gift_form: function() {
			this.clear_elements();
			this.clear_buttons();
			$('#gift-form').removeClass('d-none');
		},
		show_wishlist_form: function() {
			this.clear_elements();
			this.clear_buttons();
			$('#wishlist-form').removeClass('d-none');
		},
		get_users: function() {
			let app = this;
			axios.get('http://info3103.cs.unb.ca:36371/users')
			.then(function (response) {
				app.users = response.data.users;
			})
			.catch(function(error) {
				$('#login-input-2 + .invalid-feedback').show();
				$('#pw-input-2 + .invalid-feedback').show();
				return [];
			});
		},
		register_gift: function() {
			let app = this;
			let gift_form = $('#gift-form');
			let to = gift_form.find('#to-input option:selected').text();
			let price = gift_form.find('#price-input').val();
			let item_name = gift_form.find('#giftname-input').val();

			let data = {
				to: to,
				price: price,
				item_name: item_name
			}

			axios.post('http://info3103.cs.unb.ca:36371/users/'+app.user_id+'/gifts', data)
			.then(function (response) {
				$('#gift-form').addClass('d-none');
			})
			.catch(function(error) {
				$('#login-input-2 + .invalid-feedback').show();
				$('#pw-input-2 + .invalid-feedback').show();
			});
		},
		register_wishlist: function() {
				let app = this;
				let gift_form = $('#wishlist-form');
				let to = app.user_id;
				let price = gift_form.find('#price-input-2').val();
				let item_name = gift_form.find('#giftname-input-2').val();
				let wishlisted = 1;
	
				let data = {
					to: to,
					price: price,
					item_name: item_name,
					wishlisted: wishlisted
				}
	
				axios.post('http://info3103.cs.unb.ca:36371/users/'+app.user_id+'/gifts', data)
				.then(function (response) {
					$('#wishlist-form').addClass('d-none');
				})
				.catch(function(error) {
					$('#login-input-2 + .invalid-feedback').show();
					$('#pw-input-2 + .invalid-feedback').show();
				});
		},
		clear_elements: function() {
			$('div[id$="-form"]').addClass('d-none');
			$('div[id$="-list"]').addClass('d-none');
		},
		clear_buttons: function() {
			$('label.active').removeClass('active');
		},
		confirm_gift_received: function(gift) {
			let app = this;
			data = { gift_id: gift.gift_id }
			
			axios.post('http://info3103.cs.unb.ca:36371/gifts/actions/receive', data)
			.then(function (response) {
				gift.received = true;
			})
			.catch(function(error) {
				console.log('an error occurred');
			});
		},
		show_users_list: function() {
			this.clear_elements();
			this.clear_buttons();
			$('#user-list').removeClass('d-none');
		},
		send_gift: function(gift) {
			let app = this;
			data = { gift_id: gift.gift_id }
			
			axios.post('http://info3103.cs.unb.ca:36371/wishlist/actions/send', data)
			.then(function (response) {
				gift.from_user = app.user_id;
			})
			.catch(function(error) {
				console.log('an error occurred');
			});
		}
	}

});
