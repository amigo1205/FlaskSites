$(document).ready(function() {

    so = {};
    
    window.app.getJSON({
        url: '/getAdvertisingCoordinators',
        completionHandler: function(result) {
            so.advertisingCoordinators = result.data;
            $('#modal-trigger').removeAttr('disabled');
            $('#coordinatorList-notmodal-trigger').removeAttr('disabled');

            so.advertisingCoordinators.forEach(function (coord) {
                $('#providers-notmodal-info').append(
                    '<div class="col-xs-12 col-sm-6 top-25">' +
                        '<p style="text-transform: capitalize;">' + '<strong>' + coord.organization + '</strong></p>' +
                        '<p style="text-transform: capitalize;">' +
                            coord.firstName + ' ' + coord.lastName + '<br />' +
                            coord.address1 + '<br />' +
                            (coord.address2.length ? (coord.address2 + '<br />') : '') +
                            coord.city + ', ' + coord.province + ', ' + '<span style="text-transform: uppercase;">' + coord.postal + '</span><br />' +
                            'Ph: ' + coord.phone + '<br />' +
                            (coord.fax.length ? 'Fax: ' + coord.fax + '<br />' : '') +
                            '<span style="text-transform: none;">' + coord.email + '</span>' +
                        '</p>' +
                    '</div>'
                );
            });




        },
        errorHandler: function(status, responseText, res) {
            $('#modal-error').show().html('<strong>Oops!</strong> Something went wrong loading this dialog. Please close and try again.')
            console.error(res.error.message);
        }
    })

    if (app.coordinator_email.length) {
        $('.intro-btn-2 span').html('<i class="fa fa-home" aria-hidden="true"></i> Provider Dashboard');
        $('.intro-btn-2').css('left', function(i, oldVal) { return parseInt(oldVal) + 13; });
    }

    $('#provider-locator').on('shown.bs.modal', function() {
        if (!$('#providers-modal-info').children().length) {
            so.advertisingCoordinators.forEach(function (coord) {
                $('#providers-modal-info').append(
                    '<div class="col-xs-12 col-sm-6 top-25">' +
                        '<p style="text-transform: capitalize;">' + '<strong>' + coord.organization + '</strong></p>' +
                        '<p style="text-transform: capitalize;">' +
                            coord.firstName + ' ' + coord.lastName + '<br />' +
                            coord.address1 + '<br />' +
                            (coord.address2.length ? (coord.address2 + '<br />') : '') +
                            coord.city + ', ' + coord.province + ', ' + '<span style="text-transform: uppercase;">' + coord.postal + '</span><br />' +
                            'Ph: ' + coord.phone + '<br />' +
                            (coord.fax.length ? 'Fax: ' + coord.fax + '<br />' : '') +
                            '<span style="text-transform: none;">' + coord.email + '</span>' +
                        '</p>' +
                    '</div>'
                );
            });
        }
    });

    $('#footer-copyright').hide();
});