
$(document).ready(function() {
    onCallGet();

});

var onCallGet = function() {
    var element = $('#content');
    app.showSpinner('onCall', element);
    window.app.getJSON({
        url: '/getDoctorOnCall',
        completionHandler: checkOnCallDoctorsSuccess,
        errorHandler: function(status, responseText, err) {
            // 500 error handling
            app.hideSpinner('onCall');
            $("#floating-alert").show();
            $("#floating-alert-text").html("<strong>Oops!</strong> We seem to have lost connection. Please refresh the page in a few moments.");
            if (err) console.error(err.error.message);
        }
    });
};

var checkOnCallDoctorsSuccess = function(result) {
    app.hideSpinner('onCall');
    result.data.forEach(function(doc) {
        // Comment out until we have scheduling
        // var endDate = new Date(doc.onCallEndTime);
        $('#on-call-doctors').append(
            '<div class="col-xs-12 col-sm-6 col-md-12 col-lg-6 col-centered" style="padding-top: 15px;">' +
                '<p><strong>' + doc.name + '</strong></p>' +
                '<p>' +
                    'Ph: ' + doc.cellPhone + '<br />' +
                    doc.email +
                '</p>' +
                /* Comment out until we have scheduling
                '<p>' +
                    'Until: <strong>' + endDate.getUTCHours() + ':' + endDate.getMinutes() + '</strong><br />' +
                '</p>' +*/
            '</div>'
        );
    });
    setTimeout(function() {
        $('#on-call-doctors').html('');
        onCallGet();
    }, 60000);
};