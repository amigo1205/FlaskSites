    $(document).ready(function() {

        $.validate({
            form : '#set-password-form',
            modules : 'security, toggleDisabled',
            disabledFormFilter : 'form.toggle-disabled',
        });


        var path = window.location.pathname.split("/");
        var coordinatorId = path[2];
        var activation = path[3];
        var element = $('#set-password-form');
        window.app.showSpinner('setPasswordForm', element);

        window.app.postJSON({
            url: '/resetPasswordActivation',
            data: JSON.stringify({'coordinatorId': coordinatorId, 'emailActivation': activation}),
            completionHandler: function(result) {
                if (result.data.status == "ACTIVE" || result.data.status == "UNAUTHORIZED") {
                    $('#set-password-form').show();
                } else {
                    $('#set-password-not-valid').show();
                }
                window.app.hideSpinner('setPasswordForm', element);
            },
            errorHandler: function(status, responseText, err ) {
                if (err) {
                    if (status == 500) {
                        $('#set-password-not-valid').show().html("<strong>Oops!</strong> It seems our password service is down. Please try again later.");
                        console.log(err.error.message);
                    }
                    else {
                        errorMessage = err.error.message;
                        $('#set-password-not-valid').show().html(errorMessage)
                    }
                }
                else {
                    $("#floating-alert").show();
                    $("#floating-alert-text").html("<strong>Oops!</strong> We seem to have lost connection. Please refresh the page in a few moments.");
                }
                window.app.hideSpinner('setPasswordForm', element);
            }
        });

        $('#set-password-form').on('submit', function(e) {
            e.preventDefault();
            var element = $('#set-password-form');
            window.app.showSpinner('setPasswordForm', element);
            $('#fail-message').hide();



            var password = $(this).find('input[name="password"]').val();

            var data = JSON.stringify({'password': password, 'coordinatorId': coordinatorId, 'emailActivation':activation });

            window.app.postJSON({
                url: '/resetPasswordActivate',
                data: data,
                completionHandler: function(result) {
                    if (result.success == true) {
                        $('#set-password-form').hide();
                        $('#set-password-success-message').show();
                        //window.location.assign('/login');
                    } else {
                        $('#fail-message').show();
                        $('#fail-message').text("Error : " + result.error.message + ". Please try again.");
                    }
                    window.app.hideSpinner('setPasswordForm', element);

                },
                errorHandler: function(status, responseText, err) {
                    if (err) {
                        if (status == 500) {
                            $('#set-password-not-valid').show().html("<strong>Oops!</strong> It seems our password service is down. Please try again later.");
                            console.log(err.error.message);
                        }
                        else {
                            errorMessage = err.error.message;
                            $('#set-password-not-valid').show().html(errorMessage)
                        }
                    }
                    else {
                        $("#floating-alert").show();
                        $("#floating-alert-text").html("<strong>Oops!</strong> We seem to have lost connection. Please refresh the page in a few moments.");
                    }
                    window.app.hideSpinner('setPasswordForm', element);
                }
            });

        });

    });