$(document).ready(function() {

    $("#user-not-logged-in-menu").hide();
    $("#collapse-toggle-button").hide();

    $.validate({
        form: '#login-form, #login-reset-form',
        modules : 'location, date, security',
    });

    $('#login-form').on('submit', function(e) {
        e.preventDefault();
        var element = $('#login-form');
        window.app.showSpinner('loginForm', element);


        var email = $(this).find('input[name="email"]').val();
        var password = $(this).find('input[name="password"]').val();

        var data = JSON.stringify({'email': email, 'password': password, 'ajaxURL': window.location.href });

        window.app.postJSON({
            url: '/signIn',
            data: data,
            completionHandler: function(result) {
                $('#login-error').hide()
                var destination = window.location.pathname
                if( destination == '/login' )
                    destination = '/dashboard'
                window.app.hideSpinner('loginForm', element);

                window.location.assign(destination);

            },
            errorHandler: function(status, responseText, err) {
                if (err) {
                    if (status == 500) {
                        $('#login-error').show().html("<strong>Oops!</strong> Something went wrong. Please try again later.");
                        if (err) console.error(err.error.message);
                    }
                    else
                        $('#login-error').show().html(err.error.message)
                }
                else {
                    $("#floating-alert").show();
                    $("#floating-alert-text").html("<strong>Oops!</strong> We seem to have lost connection. Please try again in a few moments.");
                }
                window.app.hideSpinner('loginForm', element);

            }
        });

    });

    $('#reset-password').off('click.resetpass').on('click.resetpass', function(e) {
        $('#login-form').hide();
        $('#login-reset-form').show();
        $('#reset-password-email-success-message').hide();

    });

    $('#login-reset-form').on('submit', function(e) {
        e.preventDefault();
        var element = $('#login-reset-form');
        window.app.showSpinner('loginResetForm', element);

        var email = $(this).find('input[name="email"]').val();
        var data = JSON.stringify({'email': email });

        window.app.postJSON({
            url: '/resetPassword',
            data: data,
            completionHandler: function(result) {
                $('#login-form').show();
                $('#login-reset-form').hide();
                $('#reset-password-email-success-message').show();
                $('#reset-error').hide();
                $("#reset-password-email-success-message span.email").text(email);
                window.app.hideSpinner('loginResetForm', element);

            },
            errorHandler: function(status, responseText, err) {
                if (err) {
                    if (status == 400)
                        $('#reset-error').show().text("That email address has not yet been activated.")
                    else if (status == 401)
                        $('#reset-error').show().text("That email address is not yet in our system.")
                    else {
                        $('#reset-error').show().html("<strong>Oops!</strong> Something went wrong. Please try again later.");
                        console.error(err.error.message);
                    }
                }
                else {
                    $("#floating-alert").show();
                    $("#floating-alert-text").html("<strong>Oops!</strong> We seem to have lost connection. Please try again in a few moments.");
                }
                window.app.hideSpinner('loginResetForm', element);
            }
        });



    });

    $('#login-reset-form').find('#login').click(function(){
        $('#login-form').show();
        $('#login-reset-form').hide();
    });

});