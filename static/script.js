var app=new Vue({
	el: '#app',
	data: {
		login: false,
		gifts: [],
		user_id: '',
		users: []
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
				if (response.data['status'] == 'success') {
					app.login = true;
					app.user_id = response.data.username;
				}
			})
			.catch(function(error) {
				if (error.response.data['status'] == 'fail') {
					app.login = false;
				}
			});
		},
		log_user: function() {
			$('#register-form').addClass('d-none');
			if (!this.login) {
				$('#login-form').removeClass('d-none');
			} else {
				this.logout_user();
			}
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
			$('#login-form').addClass('d-none');
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
		show_gifts: function(sent) {
			// check if user is logged in
			let app = this;
			if (this.login) {
				q = sent ? '?sent=true' : '';
				axios.get('http://info3103.cs.unb.ca:36371/users/' + app.user_id + '/gifts' + q)
				.then(function (response) {
					app.gifts = response.data.gifts;
					$('#gift-list').removeClass('d-none');
					$('#gift-form').addClass('d-none');
				})
				.catch(function(error) {
					console.log('an error occurred');
				});
			}
		},
		show_gifts_sent: function() {
			let app = this;
			app.show_gifts(true);
		},
		show_gifts_received: function() {
			let app = this;
			app.show_gifts(false);
		},
		show_gift_form: function() {
			$('#gift-list').addClass('d-none');
			$('#gift-form').removeClass('d-none');
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
		}
	}

});
