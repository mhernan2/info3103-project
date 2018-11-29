var app=new Vue({
	el: '#app',
	data: {
		login: false
	},

	created: function () {
		this.check_login();
	},

	methods:{
		check_login: function() {
			let app = this;
			axios.get('http://info3103.cs.unb.ca:36371/login')
			.then(function (response) {
				if (response.data['status'] == 'success') {
					app.login = true;
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
			let password = register_form.find('#password-input-2').val();

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
		}
	}

});
