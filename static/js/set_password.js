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
            url: '/validateActivation',
            data: JSON.stringify({'coordinatorId': coordinatorId, 'emailActivation': activation}),
            completionHandler: function(result) {
               $('#set-password-form').show();
                window.app.hideSpinner('setPasswordForm', element);

            },
            errorHandler: function(status, responseText, err) {
                if (err) {
                    if (status == 500)
                        $('#set-password-not-valid').show().html("<strong>Oops!</strong> It seems our activation service is down. Please try again later.");
                    else
                        $('#set-password-not-valid').show().html(err.error.message);
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

            var password = $(this).find('input[name="password"]').val();

            var data = JSON.stringify({'password': password, 'coordinatorId': coordinatorId, 'emailActivation':activation});

            window.app.postJSON({
                url: '/activate',
                data: data,
                completionHandler: function(result) {
                    $('#set-password-form').hide();
                    $('#set-password-success-message').show();
                    window.app.hideSpinner('setPasswordForm', element);

                },
                errorHandler: function(status, responseText, err) {
                    if (err) {
                        if (status == 500)
                            $('#set-password-not-valid').show().html("<strong>Oops!</strong> It seems our activation service is down. Please try again later.");
                        else
                            $('#set-password-not-valid').show().html(err.error.message);
                    }
                    else {
                        $('#set-password-not-valid').show().html("<strong>Oops!</strong> It seems we've lost connection. Please try again later.");
                    }
                    window.app.hideSpinner('setPasswordForm', element);

                }
            });
        });
    });