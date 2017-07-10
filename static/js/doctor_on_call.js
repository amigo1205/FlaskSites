$(document).ready(function() {

    $('[data-toggle="tooltip"]').tooltip();

    var doctorsTable = $('.doctors-oncall-table');

    var createNewRow = function(item) {
        return row = $('<tr data-doctor-id="'+ item.doctorId+'">').append(
                $('<td style="text-align:center">').html('<input type="checkbox" name="oncall" class="oncall-item"  id="on-call-' + item.doctorId + '" '+ item.checked + ' />'),
                $('<td class="item-name">').text(item.name),
                $('<td class="item-email">').text(item.email),
                $('<td class="item-cell-phone">').text(item.cellPhone),
                $('<td style="text-align:center">').html('<input type="checkbox" name="receive-email" class="receive-email-item"  id="receive-email-' + item.doctorId + '" '+ item.receiveEmailChecked + ' />'),
                $('<td style="text-align:center">').html('<input type="checkbox" name="receive-text" class="receive-text-item"  id="receive-text-' + item.doctorId + '" '+ item.receiveTextChecked + ' />'),

                $('<td>').html(
                    '<a class="btn btn-info edit-item">'+
                        '<i class="fa fa-pencil" aria-hidden="true"></i>'+
                        '<span translate> Edit</span>'+
                    '</a>'),
                $('<td>').html(
                    '<a class="btn btn-warning remove-item">'+
                        '<i class="fa fa-times" aria-hidden="true"></i>'+
                        '<span translate> Delete</span>'+
                    '</a>')
                );

    };

    window.app.showSpinner('setDrOncall', doctorsTable);

    var thead = $(doctorsTable).find('thead');

    window.app.getJSON({
        url: '/getDoctors',
        data: null,
        completionHandler: function(result) {
        console.log(result);
             $.each(result.data, function (i, item) {
                var checked = (item.onCall == 1) ? 'checked' : '';
                var receiveEmailChecked = (item.receiveEmail == 'T') ? 'checked' : '';
                var receiveTextChecked = (item.receiveText == 'T') ? 'checked' : '';
                var row = createNewRow({
                    'doctorId' : item.doctorId,
                    'name' :item.name,
                    'email' : item.email,
                    'cellPhone' : item.cellPhone,
                    'checked' : checked ,
                    'receiveEmailChecked' : receiveEmailChecked ,
                    'receiveTextChecked' : receiveTextChecked
                });

                $(row).appendTo(thead);

                configureTableItem($(row));

            });

            //dataespRepeatDigest();
            window.app.hideSpinner('setDrOncall', doctorsTable);
        },
        errorHandler: function(status, responseText, err) {
            window.app.hideSpinner('setDrOncall', doctorsTable);
        }
    });


    var configureTableItem = function(item) {
        var doctorId = $(item).attr('data-doctor-id');

        $(item).find('.oncall-item').off('click').on('click', function(e) {
            e.preventDefault();
            window.app.showSpinner('oncallDoctor', doctorsTable);

            var onCall = 0;
            if( e.currentTarget.checked )
                onCall = 1
            var data = JSON.stringify({ doctorId:doctorId , onCall:onCall });

            window.app.postJSON({
                url: '/setDoctorOnCallById',
                data: data,
                completionHandler: function(result) {
                    var v = $('#on-call-'+doctorId);
                    // First remove all checked attr from Doctors Table
                    $(doctorsTable).find('input[name="oncall"]').prop('checked', false);

                    if( onCall == 1 ){
                        $('#on-call-' + doctorId).prop('checked', true);
                        v.prop('checked', true);

                    }
                    window.app.hideSpinner('oncallDoctor', doctorsTable);

                },
                errorHandler: function(status, responseText, err) {
                    window.app.handleError('Something went wrong. Try again later.', window.app.messageFromErrorResponse(responseText),'.message-field');
                    window.app.hideSpinner('oncallDoctor', doctorsTable);

                }
            });
        });
        $(item).find('.receive-email-item').off('click').on('click', function(e) {
            e.preventDefault();
            window.app.showSpinner('receiveEmailDoctor', doctorsTable);

            var receiveEmail = 'F';
            if( e.currentTarget.checked )
                receiveEmail = 'T'
            var data = JSON.stringify({ doctorId:doctorId , receiveEmail:receiveEmail });

            window.app.postJSON({
                url: '/setDoctorReceiveEmailById',
                data: data,
                completionHandler: function(result) {
                    var v = $('#receive-email-'+doctorId);

                    if( receiveEmail == 'T' ){
                        $('#receive-email-' + doctorId).prop('checked', true);
                        v.prop('checked', true);
                    }
                    else{
                        $('#receive-email-' + doctorId).prop('checked', false);
                        v.prop('checked', false);

                    }
                    window.app.hideSpinner('receiveEmailDoctor', doctorsTable);

                },
                errorHandler: function(status, responseText, err) {
                    window.app.handleError('Something went wrong. Try again later.', window.app.messageFromErrorResponse(responseText),'.message-field');
                    window.app.hideSpinner('receiveEmailDoctor', doctorsTable);

                }
            });
        });

        $(item).find('.receive-text-item').off('click').on('click', function(e) {
            e.preventDefault();
            window.app.showSpinner('receiveTextDoctor', doctorsTable);

            var receiveText = 'F';
            if( e.currentTarget.checked )
                receiveText = 'T'
            var data = JSON.stringify({ doctorId:doctorId , receiveText:receiveText });

            window.app.postJSON({
                url: '/setDoctorReceiveTextById',
                data: data,
                completionHandler: function(result) {
                    var v = $('#receive-text-'+doctorId);

                    if( receiveText == 'T' ){
                        $('#receive-text-' + doctorId).prop('checked', true);
                        v.prop('checked', true);
                    }
                    else{
                        $('#receive-text-' + doctorId).prop('checked', false);
                        v.prop('checked', false);

                    }

                    window.app.hideSpinner('receiveTextDoctor', doctorsTable);

                },
                errorHandler: function(status, responseText, err) {
                    window.app.handleError('Something went wrong. Try again later.', window.app.messageFromErrorResponse(responseText),'.message-field');
                    window.app.hideSpinner('receiveTextDoctor', doctorsTable);

                }
            });
        });



        $(item).find('.edit-item').off('click').on('click', function(e) {
            e.preventDefault();
            var data = JSON.stringify({ doctorId:doctorId });

            window.app.postJSON({
                url: '/getDoctor',
                data: data,
                completionHandler: function(result) {
                $('#add-doctor-modal').modal('show');
                    $.each(result.data, function(name, val){
                        var $el = $('#add-doctor-modal').find('[name="'+name+'"]'),
                            type = $el.attr('type');
                            tagName = $el.prop('tagName');

                        if (tagName == 'INPUT') {
                            if (type == 'text' || type == 'email' || type == 'password' || type == 'hidden') {
                                $el.val(val);
                            } else if (type == 'checkbox') {

                                $el.prop('checked', ((val == 1 || val == 'T')? true :false) );
                            } else if (type == 'radio') {
                                $('input[value="'+val+'"]').attr('checked', 'checked');
                            }
                        } else if (tagName== 'SELECT') {
                            $el.find('option[value="'+val+'"]').prop("selected",true);

                        } else if (tagName == 'TEXTAREA') {
                            $el.val(val);
                        }
                        var form = $('#add-dr-oncall-form');
                        configureDoctorForm(form, doctorId);
                    });

                },
                errorHandler: function(status, responseText, err) {
                    window.app.handleError('Something went wrong. Try again later.', window.app.messageFromErrorResponse(responseText),'.message-field');
                }
            });
        });

        $(item).find('.remove-item').off('click').on('click', function(e) {
            e.preventDefault();
            var drName = $(item).find('td.item-name').text();
            $('#delete-doctor-modal').modal('show');
            $('#delete-doctor-modal').find('.deleted-doctor-name').text(drName);
            $('#delete-doctor-modal').find('.delete-doctor-button').off('click.clickmd.item').on('click.clickmd.item', function(e) {
                e.preventDefault();
                var element = $('#delete-doctor-modal').find('.modal-content');
                window.app.showSpinner('deleteDoctor', element);
                var data = JSON.stringify({'doctorId': doctorId});
                window.app.deleteEntity({
                    url: '/deleteDoctor/' + doctorId,
                    completionHandler: function(result) {
                        window.app.hideSpinner('deleteDoctor');
                        $('#delete-doctor-modal').modal('hide');
                        $('#delete-doctor-modal').on('hidden.bs.modal', function() {
                            $(this).find('.deleted-doctor-name').text('this doctor');
                        });
                        $(item).remove();
                    },
                    errorHandler: function(status, responseText, err) {
                        window.app.hideSpinner('deleteDoctor');
                        window.app.handleError('Something went wrong. Try again later.', window.app.messageFromErrorResponse(responseText),'.message-field');
                    }
                });
            });
        });
        return item;
    }

    $('#add-doctor').off('click').on('click', function(e) {
        $('#add-doctor-modal').modal('show');
        var form = $('#add-dr-oncall-form');
        configureDoctorForm(form);
    });

    var configureDoctorForm = function(form, doctorId) {
        // Validation
        $.validate({
            form : '#add-dr-oncall-form',
            modules : 'date, logic',
            onError : function($form) {
                $("#message-field").show();
                $("#message-field").text("Please fill all required fields highlighted in red and submit the form again.");
            },
            onSuccess : function($form) {
                addEditDoctor();
                return false;
            }
        });

        $('#add-doctor-modal').on('hidden.bs.modal', function() {
            $(this).find('form').trigger('reset');
            $("#message-field").hide();
        });

        $(form).find('input, select, textarea').on("keydown change", function(){
            $("#message-field").hide();
        });

        // Submit the Form.Add Doctor
        $('add-dr-oncall-form').on('submit', function(e) {
            e.preventDefault();
        });

        var addEditDoctor = function(){

            $("#message-field").hide();

            window.app.showSpinner('addDoctor', form);
            var formValues = {};

            $.each(form.serializeArray(), function(i, field) {
                formValues[field.name] = field.value;
            });

            formValues['onCall'] = $(form).find('input[name="onCall"]').is(':checked') ? 1 : 0;
            formValues['receiveEmail'] = $(form).find('input[name="receiveEmail"]').is(':checked') ? 'T' : 'F';
            formValues['receiveText'] = $(form).find('input[name="receiveText"]').is(':checked') ? 'T' : 'F';

            if (doctorId) {
                formValues['doctorId'] = doctorId;
                var data = JSON.stringify(formValues);
                window.app.postJSON({
                    url: '/updateDoctor',
                    data: data,
                    completionHandler: function(result) {
                        window.app.hideSpinner('addDoctor', form);
                        $('#add-doctor-modal').modal('hide');

                        if (formValues['onCall'] == 1) {
                            // First remove all checked attr from Doctors Table
                            $(doctorsTable).find('input[name="oncall"]').prop('checked', false);
                        }

                        var row = $(doctorsTable).find("tr[data-doctor-id='" + doctorId + "']");

                        $(row).find('td.item-name').text(formValues['name']);
                        $(row).find('td.item-email').text(formValues['email']);
                        $(row).find('td.item-cell-phone').text(formValues['cellPhone']);
                        $(row).find('td').find('input[name="oncall"]').prop('checked', ((formValues['onCall'] == 1)? true :false) );
                        $(row).find('td').find('input[name="receive-email"]').prop('checked', ((formValues['receiveEmail'] == 'T')? true :false) );
                        $(row).find('td').find('input[name="receive-text"]').prop('checked', ((formValues['receiveText'] == 'T')? true :false) );
                    },
                    errorHandler: function(status, responseText, err) {
                        window.app.hideSpinner('addDoctor', form);
                        window.app.handleError('Something went wrong. Try again later.', window.app.messageFromErrorResponse(responseText),'.message-field');
                    }
                });
            } else {
                var data = JSON.stringify(formValues);
                var doctorExist = false;

                $('td.item-name').each(function(e){
                    if ($(this).text() == formValues.name) {
                        doctorExist = true;
                    };
                });

                if (doctorExist) {

                    window.app.hideSpinner('addDoctor', form);
                    $("#message-field").show();
                    $("#message-field").text("This doctor name already exists in the table!");

                } else {
                    window.app.postJSON({
                        url: '/addDoctor',
                        data: data,
                        completionHandler: function(result) {
                        window.app.hideSpinner('addDoctor', form);
                            $('#add-doctor-modal').modal('hide');

                            if (result.data.onCall == 1) {
                                // First remove all checked attr from Doctors Table
                                $(doctorsTable).find('input[name="oncall"]').prop('checked', false);
                            }

                            var checked = (result.data.onCall == 1) ? 'checked' : '';
                            var receiveEmailChecked = (result.data.receiveEmail == 'T') ? 'checked' : '';
                            var receiveTextChecked = (result.data.receiveText == 'T') ? 'checked' : '';
                            var row = createNewRow({
                                'doctorId' : result.data.doctorId,
                                'name' :result.data.name,
                                'email' : result.data.email,
                                'cellPhone' : result.data.cellPhone,
                                'checked' : checked,
                                'receiveEmailChecked' : receiveEmailChecked ,
                                'receiveTextChecked' : receiveTextChecked

                            });
                            var lastRow = $(doctorsTable).find("tr:last");
                            $(lastRow).after(row);

                            configureTableItem($(row));
                        },
                        errorHandler: function(status, responseText, err) {
                            window.app.hideSpinner('addDoctor', form);
                            window.app.handleError('Something went wrong. Try again later.', window.app.messageFromErrorResponse(responseText),'.message-field');
                        }
                    });
                }

            }

        };
    }

});