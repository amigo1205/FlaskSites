$(document).ready(function() {

    $.validate({
        form : '#register-form',
        modules : 'location, date, security',
        onError : function($form) {
            $("#floating-alert").show();
            $("#floating-alert-text").html("Please fill all required fields highlighted in red and submit the form again.");
        },
    });

    $('#register-form').find('input, select, textarea').on("keydown change", function(){
        $('#fail-message').hide();
        $("#floating-alert").hide();
    });

    $('#register-form').on('submit', function(e) {

        e.preventDefault();
        $("#floating-alert").hide();
        var element = $('#register-form');
        window.app.showSpinner('registerForm', element);


        var formValues = {};
        $.each($(this).serializeArray(), function(i, field) {
            formValues[field.name] = field.value;
        });

        var regexObj = /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/;
        formValues['phone'] = formValues['phone'].replace(regexObj, "($1) $2-$3");
        formValues['fax'] = formValues['fax'].replace(regexObj, "($1) $2-$3");

        var data = JSON.stringify(formValues);
        var email = $(this).find('input[name="email"]').val();

        window.app.postJSON({
            url: '/signUp',
            data: data,
            completionHandler: function(result) {
                $('#register-form').hide();
                $('#register-success-message').show();
                $('#fail-message').hide()
                $( "#register-success-message span.email" ).text(email);
                window.app.hideSpinner('registerForm', element);

            },
            errorHandler: function(status, responseText, err) {
                if (err) {
                    if (status == 500) {
                        $('#fail-message').show().html("<strong>Oops!</strong> It seems our registration service is down. Please try again later.");
                        console.log(err.error.message);
                    }
                    else
                        $('#fail-message').show().text(err.error.message);
                }
                else {
                    $("#floating-alert").show();
                    $("#floating-alert-text").html("<strong>Oops!</strong> We seem to have lost connection. Please try again in a few moments.");
                }
                window.app.hideSpinner('registerForm', element);

            }
        });

    });

});