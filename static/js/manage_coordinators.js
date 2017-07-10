$(document).ready(function() {
    var coordinatorsTable = $('.manage-coordinators-table');
    var coordinators = [];

    var createCheckBoxes = function(item) {
        var checkBoxes = {
            includeInProviderList : (item.includeInProviderList == 'T') ? '<i class="fa fa-check"></i>' : '',
            canAuthorizeNewProviders : (item.admin == 'T') ? '<i class="fa fa-check"></i>' : ''
        };

        return checkBoxes;
    }

    var createNewRow = function(item) {

        var checkBoxes = createCheckBoxes(item);

        return row = $('<tr data-coordinator-id="'+ item.coordinatorId+'">').append(
                $('<td class="item-first-name">').text(item.firstName),
                $('<td class="item-last-name">').text(item.lastName),
                $('<td class="item-email">').text(item.email),
                $('<td class="item-organization">').text(item.organization),
                $('<td class="item-canAuthorizeNewProviders" style="text-align:center">').html(checkBoxes.canAuthorizeNewProviders),
                $('<td class="item-includeInProviderList" style="text-align:center">').html(checkBoxes.includeInProviderList),
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

    window.app.showSpinner('manageCoordinators', coordinatorsTable);

    var thead = $(coordinatorsTable).find('thead');

    window.app.getJSON({
        url: '/getCoordinators',
        data: null,
        completionHandler: function(result) {
        console.log(result);
        coordinators = result.data;
             $.each(result.data, function (i, item) {
                var row = createNewRow({
                    'coordinatorId' : item.coordinatorId,
                    'firstName' :item.firstName,
                    'lastName' :item.lastName,
                    'email' : item.email,
                    'organization' : item.organization,
                    'includeInProviderList' : item.includeInProviderList ,
                    'admin' : item.admin
                });

                $(row).appendTo(thead);

                configureTableItem($(row));

            });

            window.app.hideSpinner('manageCoordinators', coordinatorsTable);
        },
        errorHandler: function(status, responseText, err) {
            window.app.hideSpinner('manageCoordinators', coordinatorsTable);
        }
    });

    var configureTableItem = function(item) {

        var coordinatorId = $(item).attr('data-coordinator-id');
        var coordinator = {};

        for (var i=0; i< coordinators.length; i++) {
            if (coordinators[i].coordinatorId == coordinatorId) {
                coordinator = coordinators[i];
            }
        }

        $(item).find('.edit-item').off('click').on('click', function(e) {
            e.preventDefault();
            $('#edit-coordinator-modal').modal('show');
            $.each(coordinator, function(name, val){

                var $el = $('#edit-coordinator-modal').find('[name="'+name+'"]'),
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
                var form = $('#edit-coordinator-form');
                configureCoordinatorForm(form, coordinator);
            });

        });

        $(item).find('.remove-item').off('click').on('click', function(e) {
            e.preventDefault();
            var firstName = $(item).find('td.item-first-name').text();
            var lastName = $(item).find('td.item-last-name').text();

            var coordinatorName = firstName + " " + lastName;
            var modal = '#delete-coordinator-modal';
            $(modal).modal('show');
            $(modal).find('.deleted-coordinator-name').text(coordinatorName);
            $(modal).find('.delete-coordinator-button').off('click.clickmd.item').on('click.clickmd.item', function(e) {
                e.preventDefault();
                var element = $(modal).find('.modal-content');

                window.app.showSpinner('deleteCoordinator', element);
                var data = JSON.stringify({'coordinatorId': coordinatorId});

                window.app.deleteEntity({
                    url: '/deleteCoordinator/' + coordinatorId,
                    completionHandler: function(result) {
                        window.app.hideSpinner('deleteCoordinator');
                        $(modal).modal('hide');
                        $(modal).on('hidden.bs.modal', function() {
                            $(this).find('.deleted-coordinator-name').text('this coordinator');
                        });
                        $(item).remove();
                    },
                    errorHandler: function(status, responseText, err) {
                        window.app.hideSpinner('deleteCoordinator');
                        window.app.handleError('Something went wrong. Try again later.', window.app.messageFromErrorResponse(responseText),'.message-field');
                    }
                });
            });
        });

        return item;
    }



    var configureCoordinatorForm = function(form, coordinator) {
        // Validation
        $.validate({
            form : form,
            modules : 'date, logic',
            onError : function($form) {
                $("#message-field").show();
                $("#message-field").text("Please fill all required fields highlighted in red and submit the form again.");
            },
            onSuccess : function($form) {
                editCoordinator();
                return false;
            }
        });

        $('#edit-coordinator-modal').on('hidden.bs.modal', function() {
            $(this).find('form').trigger('reset');
            $("#message-field").hide();
        });

        $(form).find('input, select, textarea').on("keydown change", function(){
            $("#message-field").hide();
        });

        // Submit the Edit Coordinator Form.
        $(form).on('submit', function(e) {
            e.preventDefault();
        });

        var editCoordinator = function(){

            $("#message-field").hide();

            window.app.showSpinner('editCoordinator', form);
            //var coordinator = {};

            $.each(form.serializeArray(), function(i, field) {
                coordinator[field.name] = field.value;
            });

            coordinator['receiveAppointmentText'] = $(form).find('input[name="receiveAppointmentText"]').is(':checked') ? 'T' : 'F';
            coordinator['receiveErrorText'] = $(form).find('input[name="receiveErrorText"]').is(':checked') ? 'T' : 'F';
            coordinator['receiveErrorEmails'] = $(form).find('input[name="receiveErrorEmails"]').is(':checked') ? 'T' : 'F';
            coordinator['receivesWaiverEmails'] = $(form).find('input[name="receivesWaiverEmails"]').is(':checked') ? 'T' : 'F';
            coordinator['includeInProviderList'] = $(form).find('input[name="includeInProviderList"]').is(':checked') ? 'T' : 'F';
            coordinator['admin'] = $(form).find('input[name="admin"]').is(':checked') ? 'T' : 'F';
            coordinator['coordinatorId'] = coordinator.coordinatorId;

            var data = JSON.stringify(coordinator);

            window.app.postJSON({
                url: '/updateCoordinator',
                data: data,
                completionHandler: function(result) {
                    window.app.hideSpinner('editCoordinator', form);
                    $('#edit-coordinator-modal').modal('hide');

                    for (var i=0; i< coordinators.length; i++) {
                        if (coordinators[i].coordinatorId == coordinator.coordinatorId) {
                            coordinators[i] = coordinator;
                        }
                    }

                    var row = $(coordinatorsTable).find("tr[data-coordinator-id='" + coordinator.coordinatorId + "']");

                    $(row).find('td.item-first-name').text(coordinator['firstName']);
                    $(row).find('td.item-last-name').text(coordinator['lastName']);
                    $(row).find('td.item-email').text(coordinator['email']);
                    $(row).find('td.item-organization').text(coordinator['organization']);

                     var checkBoxes = createCheckBoxes(coordinator);

                    $(row).find('td.item-canAuthorizeNewProviders').html(checkBoxes.canAuthorizeNewProviders);
                    $(row).find('td.item-includeInProviderList').html(checkBoxes.includeInProviderList);

                },
                errorHandler: function(status, responseText, err) {
                    window.app.hideSpinner('editCoordinator', form);
                    window.app.handleError('Something went wrong. Try again later.', window.app.messageFromErrorResponse(responseText),'.message-field');
                }
            });


        };
    }

});