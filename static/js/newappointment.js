$(document).ready(function() {

    //Enable Tooltip
    $('[data-toggle="tooltip"]').tooltip();

    // Validation
    $.validate({
        form: '#new-case-form-hi-fields',
        modules : 'date, logic, toggleDisabled',
        disabledFormFilter : 'form.toggle-disabled'
    });

    var patientFormFields= {};
    var demographicNo;
    var userName = '';
    var demographicRecord = {};
    var displayExpandedBusinessHours = false;
    var signatureDiv;

    $('#new-case-form-hi-fields').find('input, select, textarea').on("keydown change", function(){
        $('#no-user-found-container').find('.message-container').hide();
        $('#new-case-form-patient-fields').hide();
    });

    $('#hin').keydown(function() {
        $('#patient-info-display').hide();
        $('#patient-appointment-list').html("");
    })
    $('#ver').keydown( function (){
        $('#no-ver').prop('checked', false);
        $('#patient-info-display').hide();
        $('#patient-appointment-list').html("");
    })
    $('#no-ver').change( function() {
        $('#ver').val("")
        $('#patient-info-display').hide();
        $('#patient-appointment-list').html("");
    });

    updateAppointmentStatus = function(event,caseId , demographicNo , status ) {

        try { event.stopPropagation() }
        catch(err){ console.log(err)}
        postData = JSON.stringify({ caseId:caseId , demographicNo:demographicNo , status:status })
        var element = $('#new-case-form-hi-fields');
        window.app.showSpinner('updateAppointmentStatus', element);

        window.app.postJSON({
            url: '/updateAppointmentStatus' ,
            data: postData ,
            completionHandler: function(result) {
                displayAppointments( result.data.currentAppointments )
                displayAppointmentsPast( result.data.pastAppointments )
                window.app.hideSpinner('updateAppointmentStatus' );

            },
            errorHandler: function(status, responseText, err) {
                $("#floating-alert").show();
                $("#floating-alert-text").html("<strong>Oops!</strong> It seems we lost connection. Please refresh the page in a few moments. (msg1)");
                if (err) console.log(err.error.message);
                window.app.hideSpinner('updateAppointmentStatus' );

            }
        });
    }
    displayAppointments = function( result ){
        $('#patient-appointments').hide();
        $('#patient-appointment-list').html("");

        if (result.length) {
            $('#patient-appointments').show();
            $('#patient-appointments strong').replaceWith('<strong>Pending Appointments</strong>');
            $('#patient-appointment-list').html("");
            result.forEach(function (v, i) {
//                var appointmentStartDate = new Date(v.appointmentStartDate);
//                var appointmentEndDate = new Date(v.appointmentEndDate);
                var appointmentStartDate = v.appointmentStartDate;
                var appointmentEndDate = v.appointmentEndDate;
                var todayDate = new Date();
                var isToday = false;
                var appointmentDuration = v.appointmentDuration
                //if (todayDate.getFullYear() == appointmentStartDate.getFullYear() && todayDate.getMonth() == appointmentStartDate.getMonth() && todayDate.getDate() == appointmentStartDate.getDate())
//                    isToday = true;





                var appointmentRow = '<div class="panel-group" id="accordion">'+
                                        '<div class="panel panel-default" id="panel' + i + '">'+
                                            '<div class="panel-heading">';

                appointmentRow +=
                                                ' <h4 class="row panel-title">' +
                                                    '<div class="col-sm-6 text-left" style="min-height: 26px;">'+
                                                        '<a role="button" data-toggle="collapse" data-parent="#patient-appointment-list" style="color:#333; font-size:14px;" data-target="#appointment' + i + '">' +
    '<i id="expand' + i + '" class="fa fa-plus-square-o" style="margin-right:8px;"></i>' +
                                                            '<span class="" id="appointment-time' + i + '">' +
                                                        ( isToday ? "Today - " + appointmentStartDate : appointmentStartDate) +
                                                            " (" + appointmentDuration + " min)";
                                                            if(v.status == 't' )
                                                                appointmentRow += '</span>';
                                                            else if(v.status == 'C' )
                                                                appointmentRow += ' - Cancelled </span>';
                                                            else if(v.status == 'N' )
                                                                appointmentRow += ' - No Show</span>';
                                                            else
                                                                appointmentRow += ' - status=' + v.status + '</span>';
                                                            appointmentRow +=
                                                        '</a>'+
                                                    '</div>'+
                                                    '<div class="col-sm-6 text-right">';
                                                    if(v.status == 't' )
                                                        appointmentRow +=
                                                            '<button onclick="updateAppointmentStatus(event,'+ v.caseId + ',' + demographicRecord['demographicNo'] + ',\'N\')" class="btn btn-info no-show-item" type="button"  aria-hidden="true"><i class="fa fa-ban" aria-hidden="true"></i> No Show</button>&nbsp;' +
                                                            '<button  onclick="updateAppointmentStatus(event,'+ v.caseId + ',' + demographicRecord['demographicNo'] + ',\'C\')" type="button" class="btn btn-warning cancel-item"  aria-hidden="true"><i class="fa fa-times" aria-hidden="true"></i> Cancel</button>';
                                                    else if(v.status == 'C' )
                                                        appointmentRow +=
                                                            '<button onclick="updateAppointmentStatus(event,'+ v.caseId + ',' + demographicRecord['demographicNo'] + ',\'t\')" class="btn btn-default undo-item"> Undo Cancel</button>';
                                                    else if(v.status == 'N' )
                                                        appointmentRow +=
                                                            '<button onclick="updateAppointmentStatus(event,'+ v.caseId + ',' + demographicRecord['demographicNo'] + ',\'t\')" class="btn btn-default undo-item"> Undo No Show</button>';
                                                    else
                                                        appointmentRow +=
                                                            ' <button onclick="updateAppointmentStatus(event,'+ v.caseId + ',' + demographicRecord['demographicNo'] + ',\'t\')" class="btn btn-default undo-item"> Undo</button>';

                                            appointmentRow +=
                                                    '</div>'
                                                '</h4>';
                appointmentRow += '</div>';
                appointmentRow +=
                                    '<div id="appointment' + i + '" class="panel-collapse collapse">'+
                                        '<div class="panel-body">' +
                                            '<p style="margin-bottom: 20px;"><span class="pull-right" style="margin-left: 1em;"></span>' +
                                            '<strong>Reason:</strong> ' + (v.reason.length ? v.reason : '(none)') + '</p>' +
                                            '<span><strong>' + v.organization + '</strong><br />' + v.firstName + ' ' + v.lastName + '<br />' +
                                        '</div>'+
                                    '</div>';
                appointmentRow +=
                                '</div>' +
                             '</div>';

                $('#patient-appointment-list').append( appointmentRow );

                $('#appointment' + i).on('show.bs.collapse', function () {
                    $('#expand' + i).removeClass('fa-plus-square-o').addClass('fa-minus-square-o');
                    $('#appointment-time' + i).addClass('text-success bold');
                });
                $('#appointment' + i).on('hide.bs.collapse', function () {
                    $('#expand' + i).removeClass('fa-minus-square-o').addClass('fa-plus-square-o');
                    $('#appointment-time' + i).removeClass('text-success bold');
                });
            })
        }
        else
            $('#patient-appointments strong').replaceWith('<strong class="text-info">No pending appointments found</strong>');
        $('#patient-appointments').show();
        $('#patient-appointments strong').show();

    }



    displayAppointmentsPast = function( result ){
        $('#patient-appointments-past').hide();
        $('#patient-appointment-list-past').html("");

        if (result.length) {
            $('#patient-appointments-past').show();
            $('#patient-appointments-past strong').replaceWith('<strong>Past Appointments</strong>');
            $('#patient-appointment-list-past').html("");
            result.forEach(function (v, i) {
                var appointmentStartDate = v.appointmentStartDate;
                var appointmentEndDate = v.appointmentEndDate;
                var appointmentDuration = v.appointmentDuration


                var appointmentRow = '<div class="panel-group" id="accordion">'+
                                        '<div class="panel panel-default" id="panel' + i + '">'+
                                            '<div class="panel-heading">';


                appointmentRow +=
                                                ' <h4 class="row panel-title">' +
                                                    '<div class="col-sm-6 text-left" style="min-height: 26px;">'+
                                                        '<a role="button" data-toggle="collapse" data-parent="#patient-appointment-list-past" style="color:#333; font-size:14px;" data-target="#appointmentpast' + i + '">' +
                                                            '<i id="expandpast' + i + '" class="fa fa-plus-square-o" style="margin-right:8px;"></i>' +
                                                            '<span class="" id="past-appointment-time' + i + '">' +

                                                                appointmentStartDate +
                                                                " (" + appointmentDuration + " min)";
                                                            if (v.status == 't')
                                                                appointmentRow += '</span>'
                                                            else if(v.status == 'C' )
                                                                appointmentRow += ' - Cancelled</span>';
                                                            else if(v.status == 'N' )
                                                                appointmentRow += ' - No Show</span>';
                                                            else
                                                                appointmentRow += ' - status=' + v.status + '</span>';
                                                            appointmentRow +=
                                                        '</a>'+
                                                    '</div>'+
                                                    '<div class="col-sm-6 text-right">';

                                                if(v.status == 't' )
                                                    appointmentRow +=
                                                        '<button onclick="updateAppointmentStatus(event,'+ v.caseId + ',' + demographicRecord['demographicNo'] + ',\'N\')" class="btn btn-info no-show-item" type="button"  aria-hidden="true"><i class="fa fa-ban" aria-hidden="true"></i> No Show</button>&nbsp;';
                                                else if(v.status == 'C' )
                                                    appointmentRow += ''
                                                else if(v.status == 'N' )
                                                    appointmentRow +=
                                                        '<button  onclick="updateAppointmentStatus(event,'+ v.caseId + ',' + demographicRecord['demographicNo'] + ',\'t\')" class="btn btn-default undo-item"> Undo No Show</button>';
                                                else
                                                    appointmentRow +=''

                        appointmentRow +=
                                                    '</div>'
                                                '</h4>';
                        appointmentRow += '</div>';

                        appointmentRow +=
                                            '<div id="appointmentpast' + i + '" class="panel-collapse collapse">' +
                                                '<div class="panel-body">' +
                                                    '<p style="margin-bottom: 20px;"><span class="pull-right" style="margin-left: 1em;"></span>' +
                                                    '<strong>Reason:</strong> ' + (v.reason.length ? v.reason : '(none)') + '</p>' +
                                                    '<span><strong>' + v.organization + '</strong><br />' + v.firstName + ' ' + v.lastName + '<br />' +
                                                '</div>'
                                            '</div>';
                        appointmentRow +=
                                        '</div>' +
                                     '</div>';

                $('#patient-appointment-list-past').append( appointmentRow );


                $('#appointmentpast' + i).on('show.bs.collapse', function () {
                    $('#expandpast' + i).removeClass('fa-plus-square-o').addClass('fa-minus-square-o');
                    $('#past-appointment-time' + i).addClass('text-success bold');
                });
                $('#appointmentpast' + i).on('hide.bs.collapse', function () {
                    $('#expandpast' + i).removeClass('fa-minus-square-o').addClass('fa-plus-square-o');
                    $('#past-appointment-time' + i).removeClass('text-success bold');
                });
            })
        }
        else
            $('#patient-appointments-past strong').replaceWith('');
        $('#patient-appointments-past').show()
        $('#patient-appointments-past strong').show()


    }

    toggleBusinessHours = function(){
        displayExpandedBusinessHours = !displayExpandedBusinessHours;
        updateAppointmentTable()
    }


    getAvailableAppointmentsForWeek = function( weekOfDate ){
        window.app.showSpinner('getAppointments', $('#patient-form'));

        postData = {date:weekOfDate }
        window.app.postJSON({
            url: '/getAvailableAppointmentTimes' ,
            data: JSON.stringify(postData),
            completionHandler: function(result) {
                demographicRecord["availableAppointments"] = result.data
                updateAppointmentTable()
                window.app.hideSpinner('getAppointments');
            },
            errorHandler: function(status, responseText, err) {
                window.app.hideSpinner('getAppointments');
                if (status == 403)
                    $("#appointment-creation-error").show().text("Your session has expired. Please notify your coordinator and refresh the page.");
                else if (status == 400)
                    $("#appointment-creation-error").show().text("There is an issue with some of the information you provided. Please review your entries and try again.");
                else {
                    $("#floating-alert").show();
                    $("#floating-alert-text").html("<strong>Oops!</strong> Our appointment service seems to be down. Please try again in a few moments. (msg2)");
                    if (err) console.log(err.error.message);
                }
            }
        });

    }

    function updateAppointmentTable() {
        $('#time-selection').html("");

        dateTokens = demographicRecord['availableAppointments'].weekOfDate.split("-")
        currentWeekDateTime = new Date(dateTokens[0], dateTokens[1]-1, dateTokens[2])
        previousWeekDateTime = new Date(dateTokens[0], dateTokens[1]-1, dateTokens[2]).addDays( -7 )
        nextWeekDateTime = new Date(dateTokens[0], dateTokens[1]-1, dateTokens[2]).addDays( 7 )

        var weekSelectionHeader = "<thead><tr><th class='previous'><span onclick='getAvailableAppointmentsForWeek(\"" + previousWeekDateTime.ourDateFormat() + "\")' ><i  class='fa fa-caret-left' aria-hidden='true'></i> Previous</span></th>";
        weekSelectionHeader += "<th style='text-align:center' colspan='" + (demographicRecord.availableAppointments['dayList'].length-1) + "' >Week of " + currentWeekDateTime.ourDateFormat() + "</th>";
        weekSelectionHeader += "<th class='next'><span onclick='getAvailableAppointmentsForWeek(\"" + nextWeekDateTime.ourDateFormat() + "\")' >Next <i class='fa fa-caret-right' aria-hidden='true'></i> </span></th></tr>";

        appointmentStartDateHour = parseInt(demographicRecord['appointmentStartDate'].split(" ")[1].split(":")[0])
        if( appointmentStartDateHour < 8 || appointmentStartDateHour >= 20 )
            displayExpandedBusinessHours = true;

        var dayHeader = "<tr><th class='schedule-header-emp'>";
        if( displayExpandedBusinessHours )
            dayHeader += "<span id='expanded-business-hours' onclick='toggleBusinessHours()'><i class='fa fa-clock-o' aria-hidden='true'></i>&nbsp;<i class='fa fa-compress' aria-hidden='true'></i></span>";
        else
            dayHeader += "<span id='regular-business-hours' onclick='toggleBusinessHours()'><i class='fa fa-clock-o' aria-hidden='true'></i>&nbsp;<i class='fa fa-expand' aria-hidden='true'></i></span>";
        dayHeader += "</th>";

        demographicRecord.availableAppointments['dayList'].forEach(function(v) {
            dayHeader += "<th class='schedule-header-cell'>" + v + "</th>";
        })
        dayHeader += "</tr></thead>";

        $('#time-selection').append(weekSelectionHeader + dayHeader);

        var rows = [];
        demographicRecord.availableAppointments['appointments'].forEach(function(slot) {
            var timeTokens = slot.time.split(":")
            var hourToken = parseInt(timeTokens[0]);
            if( displayExpandedBusinessHours || (hourToken >= 8 && hourToken < 20 )) {

                html =
                    "<tr>" +
                    "<td><strong>" + slot['time'].split(":")[0] + ":" + slot['time'].split(":")[1] + "</strong></td>";

                dateTokens = demographicRecord['availableAppointments'].weekOfDate.split("-")
                startOfWeekDateTime = new Date(dateTokens[0], dateTokens[1] - 1, dateTokens[2])

                slot['available'].forEach(function (dayAvailability, dayIndex) {
                    checkboxDateTime = new Date(startOfWeekDateTime)
                    checkboxDateTime.addDays(dayIndex)
                    checkboxDateTime.setHours(timeTokens[0], timeTokens[1], timeTokens[2])
                    checkboxDateTimeString = moment(checkboxDateTime).format("YYYY-MM-DD HH:mm:ss")
                    var faIcon = "fa-square-o";

                    if (checkboxDateTimeString == demographicRecord['appointmentStartDate'])
                        faIcon = "fa-check-square"

                    html +=
                        "<td class='text-center" + (dayAvailability == 0 ? " text-inactive" : " text-active") + "'>" +
                        "<i " +
                        "class='appointmentCheckbox fa " + faIcon +
                        "' data-appointment-day='" + (dayIndex + 1) + "' " +
                        "' data-appointment-time='" + slot.time +
                        "'></i>" +
                        "</td>";
                });

                html +=
                    "</tr>";

                rows.push(html);
            }
        });

        $('#time-selection').append('<tbody>' + rows + '</tbody>');

        //Change Appointment Date and Time

        $('td.text-active').find('.appointmentCheckbox').off('click').on('click', function() {
            $('#earliest-appointment-msg').text("Click the calendar icon to select another appointment time.");
            $('td.text-active').find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
            $(this).toggleClass('fa-check-square fa-square-o');

            var appointment_day = $(this).attr('data-appointment-day');
            var appointment_time = $(this).attr('data-appointment-time');

            dateTokens = demographicRecord['availableAppointments'].weekOfDate.split("-")
            selectedAppointment = new Date(dateTokens[0], dateTokens[1] - 1, dateTokens[2])
            selectedAppointment.addDays(appointment_day - 1)
            var timeTokens = appointment_time.split(":")
            selectedAppointment.setHours(timeTokens[0], timeTokens[1], timeTokens[2])
            demographicRecord['appointmentStartDate'] = selectedAppointment;

            demographicRecord['appointmentStartDate'] = moment(demographicRecord['appointmentStartDate']).format("YYYY-MM-DD HH:mm:ss");

            $('#patient-form').find('[name="appointmentStartDate"]').val(demographicRecord['appointmentStartDate']);
            $(".time-selection-container").slideUp( "slow" );
            console.log(demographicRecord["appointmentStartDate"]);
        });

        $('.time-selection-close').off('click').on('click', function() {
            $(".time-selection-container").slideUp("slow");
        });

        $('.expand-business-hours').off('click').on('click', function() {

        });

    }


    //Lookup existing patient
    $('#lookup-patient').on('click', function(e) {
        e.preventDefault();

        // show spinner
        var element = $('#new-case-form-hi-fields');
        window.app.showSpinner('patientForm', element);

        configurePatientForm();

        var hin = $('#new-case-form-hi-fields').find('input[name="hin"]').val();
        var ver = $('#new-case-form-hi-fields').find('input[name="ver"]').val();
        var patientHealthInsuranceData = JSON.stringify({ hin:hin , ver:ver });

        $('#patient-appointments strong').hide()
        $('#patient-name').hide();

        window.app.postJSON({
            url: '/getDemographicByHIN' ,
            data: patientHealthInsuranceData,
            completionHandler: function(result) {
                if (result.success) {
                    demographicRecord = result.data;
                    $('#patient-name').text(result.data.firstName + ' ' + result.data.lastName);
                    $('#no-user-found-container').hide();
                    $('#patient-appointments').show()
                    $('#patient-name').show();

                    window.app.postJSON({
                        url: '/getCurrentAppointments',
                        data: JSON.stringify({ demographicNo: result.data.demographicNo }),
                        completionHandler: function(result) {
                            displayAppointments(result.data.currentAppointments );
                            displayAppointmentsPast(result.data.pastAppointments );
                            window.app.hideSpinner('patientForm');
                        },
                        errorHandler: function(status, message, err) {
                            if (status == 401)
                                $('#appointment-display-error').show().text("Your session seems to have expired. Please sign in again.");
                            else {
                                $("#floating-alert").show();
                                $("#floating-alert-text").html("<strong>Oops!</strong> It seems our appointment service isn't working. Please refresh the page in a few moments. (msg3)");
                                if (err) console.log(err.error.message);
                            }
                            window.app.hideSpinner('patientForm');
                        }
                    });
                } else {
                    demographicRecord = result.data;
                    $('#no-user-found-container').show();
                    $('#patient-appointments').hide();
                    $('#patient-appointments-past').hide();
                    window.app.hideSpinner('patientForm');

                }
                $('#patient-info-display').show();
                $('#show-patient-form').show();

            },
            errorHandler: function(status, responseText, err) {
                window.app.hideSpinner('patientForm');
                $("#floating-alert").show()
                $("#floating-alert-text").html("<strong>Oops!</strong> It seems our patient service isn't working. Please refresh the page in a few moments. (msg4)");
                if (err) console.log(err.error.message);
            }
        });
    });


    // Save patient Info
    $('#show-patient-form').off('click.showPatientForm').on('click.showPatientForm', function(e) {

        showPatientForm();
    });




    var showPatientForm = function() {
        var element = $('#patient-info-display');
        window.app.showSpinner('showPatientForm', element);

        var lastName = demographicRecord["lastName"].substring(0,24);
        var firstName = demographicRecord["firstName"].substring(0,24);

        demographicRecord["userName"] = lastName +', '+ firstName;
        demographicRecord['coordinatorId'] = window.app.coordinatorData['coordinatorId']
        postData = JSON.stringify({demographicNo:demographicRecord["demographicNo"] , content:"patient_content.html" })

        window.app.postJSON({
            url: '/getLoggedOutContent' ,
            data: postData ,
            completionHandler: function(result) {
                window.app.hideSpinner('showPatientForm');
                if (result.success) {
                    $("#home-button").hide();
                    $("#user-logged-in-menu").hide();
                    $('#footer-copyright').hide();
                    $("main").html(result.data);
                    $('#patient-form-splash-page').show();
                    $('#terms-and-conditions-field').hide();
                    $('#patient-form').hide();

                    $("html, body").animate({ scrollTop: 0 }, "slow");

                    $('#patient-form-splash-page').find('#start').off('click').on('click', function(e) {
                        e.preventDefault();
                        $('#footer-copyright').show();
                        configureTermsAndConditions();
                    });


                    // This is the part where jSignature is initialized.
                    signatureDiv = $("#signature").jSignature({bgcolor:"#ddd" });
                    //var export_plugins = $signatureDiv.jSignature('listPlugins','export');

                    $('#reset-signature').bind('click', function(e){

                        signatureDiv.jSignature('reset');
                        $('#accept-terms-and-conditions').hide();
                        $('#reset-signature').hide();

                    });

                    $("#signature").bind('change', function(e){
                        $('#accept-terms-and-conditions').show();
                        $('#reset-signature').show();


                    });

                } else {
                    console.log(result);
                }
            },
            errorHandler: function(status, responseText, err) {
                window.app.hideSpinner('showPatientForm');
                $("#floating-alert").show();
                $("#floating-alert-text").html("<strong>Oops!</strong> It seems we lost connection. Please refresh the page in a few moments. (msg5)");
                if (err) console.log(err.error.message);
            }
        });
    };


    var configurePatientForm = function() {
        var form = '#new-case-form-patient-fields';

        // reset patient form
        window.app.resetForm($(form));

        // Show/Hide fields accordingly
        $('#no-user-found-container').find('.message-container').hide();
        $('#new-case-form-patient-fields').show();
        $('#new-case-form-case-fields').hide();

        // Do these changes when change any field on patient form
        $(form).find('input, select, checkbox, textarea').on("keydown change", function(){
            $('#no-user-found-container').find('.message-container').hide();
            $('#save-patient-info').show();
            $('#request-appointment').html('<i class="fa fa-floppy-o fa-clickmd" aria-hidden="true"></i> Save Patient Info <i class="fa fa-arrow-right" aria-hidden="true"></i> <i class="fa fa-user-md fa-clickmd" aria-hidden="true"></i> Request an appointment ');
        });

    }
    Date.prototype.today = function () {
        return ((this.getDate() < 10)?"0":"") + this.getDate() +"/"+(((this.getMonth()+1) < 10)?"0":"") + (this.getMonth()+1) +"/"+ this.getFullYear();
    }

    // For the time now
    Date.prototype.timeNow = function () {
         return ((this.getHours() < 10)?"0":"") + this.getHours() +":"+ ((this.getMinutes() < 10)?"0":"") + this.getMinutes() +":"+ ((this.getSeconds() < 10)?"0":"") + this.getSeconds();
    }
    Date.prototype.ourDateTimeFormat = function ( secondsString ) {

        return this.getFullYear() + "-" +
            ((this.getMonth()+1 < 10)?"0":"")+(this.getMonth()+1) +
            "-" +
            ((this.getDate() < 10)?"0":"")+(this.getDate()) + " " +
            ((this.getHours() < 10)?"0":"")+this.getHours() + ":" +
            ((this.getMinutes() < 10)?"0":"")+this.getMinutes() +
            secondsString;
    }
    Date.prototype.ourTimeFormat = function ( ) {

        return ((this.getHours() < 10)?"0":"")+this.getHours() + ":" +
            ((this.getMinutes() < 10)?"0":"")+this.getMinutes()
    }
    Date.prototype.ourDateFormat = function () {
        return this.toISOString().split( "T")[0]
    }
    Date.prototype.addDays = function(days) {
    this.setDate(this.getDate() + parseInt(days));
    return this;
};

    var configureTermsAndConditions = function() {

        $('#terms-and-conditions-field').show();
        $('#patient-form').hide();
        $('#patient-form-splash-page').hide();
        $('#accept-terms-and-conditions').hide();
        $('#reset-signature').hide();

        if (Modernizr.csscalc) {
            $('.terms-and-conditions-body').addClass('csscalc-tacbody');// supported
            $('.terms-and-conditions-body').removeClass('no-csscalc-tacbody');// not-supported
        } else {
            $('.terms-and-conditions-body').addClass('no-csscalc-tacbody');// not-supported
            $('.terms-and-conditions-body').removeClass('csscalc-tacbody');// not-supported
        }

        $('#terms-and-conditions-field').find('#accept-terms-and-conditions').off('click').on('click', function(e) {
            e.preventDefault();
            // get signature
            var signatureData = signatureDiv.jSignature('getData', 'default');

            var pdfWaiverDocument = new jsPDF('p','pt','letter');
            pdfWaiverDocument.setFontSize(pdfWaiverDocument.getLineHeight() *.75)
            var initialPageWidth = pdfWaiverDocument.internal.pageSize.width;

            var fontHeight = pdfWaiverDocument.getLineHeight();

            var waiverText = $("#waiver-text").text()
            waiverTextLines = waiverText.split("\n")
            // margin is 4 * height of font
            var x = (fontHeight*4);
            var y = (fontHeight*4);
            var lineHeight = fontHeight * 1.25
            // subtract top and bottom margins to get actual page height
            var pageHeight= pdfWaiverDocument.internal.pageSize.height - (y * 1);

            for( var l = 0 ; l < waiverTextLines.length ; l++ ){
                var splitLine = pdfWaiverDocument.splitTextToSize( waiverTextLines[l].trim() , initialPageWidth-(x*2) )
                if( waiverTextLines[l].trim().length < 50 )
                    y += lineHeight;
                for( var subLine = 0 ; subLine < splitLine.length ; subLine++ ){
                    // treat short lines as a title with a blank line preceding
                    pdfWaiverDocument.text(x,y,splitLine[subLine].trim())
                    y+= lineHeight;
                    if( y > pageHeight ){
                        pdfWaiverDocument.addPage()
                        y = (fontHeight*4)
                    }

                }

            }


            pdfWaiverDocument.addImage(signatureData, 'PNG', x, y , 250, 100);
            pdfWaiverDocument.text(x,y+175,"Signed by " + demographicRecord['firstName'] + " " + demographicRecord['lastName'] + " on " + new Date().today() + " " + new Date().timeNow())

            demographicRecord["waiverPDF"] = pdfWaiverDocument.output()
            window.app.showSpinner('getAppointments', $('#terms-and-conditions-field'));
            var currentDate = new Date();

            postData = {date:currentDate.getFullYear()+"-"+
                    (currentDate.getMonth()< 9?"0":"") + (currentDate.getMonth()+1)+"-"+
                    (currentDate.getDate()< 10?"0":"") + currentDate.getDate()+ " " +
                    (currentDate.getHours()< 10?"0":"") + currentDate.getHours() + ":" +
                    (currentDate.getMinutes()< 10?"0":"") + currentDate.getMinutes() + ":00" }
            window.app.postJSON({
                url: '/getAvailableAppointmentTimes' ,
                data: JSON.stringify(postData),
                completionHandler: function(result) {
                    var appointmentData = demographicRecord["availableAppointments"] = result.data

                    window.app.postJSON({
                        url: '/getEarliestAppointment',
                        data: JSON.stringify(postData),
                        completionHandler: function(result) {
                            console.log( "response to getEarliestAppoint is...")
                            console.log( result )

                            if (result.data) {

                                //demographicRecord['appointmentStartDate'] = new Date(result.data.replace( " ", "T")+"Z");
                                demographicRecord['appointmentStartDate'] = result.data;
                                //$("#floating-alert").show();
                                //$("#floating-alert-text").html(result.data + " converted to a date 1)" + new Date(result.data.replace( " ", "T")+"Z") );
                                configureNewPatientForm();
                                window.app.hideSpinner('getAppointments');
                            }
                        },
                        errorHandler: function(status, responseText, err) {

                        }
                    })
                },
                errorHandler: function(status, responseText, err) {
                    window.app.hideSpinner('getAppointments');
                    if (status == 403)
                        $("#appointment-creation-error").show().text("Your session has expired. Please notify your coordinator and refresh the page.");
                    else if (status == 400)
                        $("#appointment-creation-error").show().text("There is an issue with some of the information you provided. Please review your entries and try again.");
                    else {
                        $("#floating-alert").show();
                        $("#floating-alert-text").html("<strong>Oops!</strong> Our appointment service seems to be down. Please try again in a few moments. (msg6)");
                        if (err) console.log(err.error.message);
                    }
                }
            });
        });
    }

    var configureNewPatientForm = function(userName, notes) {
        var form = $('#patient-form');

        // Show/Hide Time Selection container
        $(".show-time-selection").off('click').on('click', function() {
            $(".time-selection-container").slideToggle("slow");
            $('html, body').animate({
                scrollTop: $("#cancel-appointment").offset().top
            }, 1000);
        });
        $("[name='appointmentStartDate']").off('click').on('click', function() {
            $(".time-selection-container").slideToggle("slow");
            $('html, body').animate({
                scrollTop: $("#cancel-appointment").offset().top
            }, 1000);
        });

        // Validation
        $.validate({
            form: '#patient-form',
            modules: 'date, logic',
            onError: function ($form) {
                $("#floating-alert").show();
                $("#floating-alert-text").html("Please fill all required fields highlighted in red and submit the form again.");
            }
        });

        $('#patient-form').find('input, select, textarea').on("keydown change", function () {
            $("#floating-alert").hide();
        });

        // Hide/Show fields accordingly
        $('#terms-and-conditions-field').hide();
        $('#patient-form-splash-page').hide();
        $(form).show();

        // Prepare the date of birth select box
         function prepareDateSelectBoxes (dateId, monthId, yearId) {
            $(yearId).append($('<option selected="selected" disabled/>').html('Year'));
            $(monthId).append($('<option selected="selected" disabled/>').html('Month'));
            $(dateId).append($('<option selected="selected" disabled/>').html('Day'));

            for (i = new Date().getFullYear(); i > 1900; i--) {
                $(yearId).append($('<option />').val(i).html(i));
            }

            for (i = 1; i < 13; i++) {
                $(monthId).append($('<option />').val(i).html(i));
            }
        }

        prepareDateSelectBoxes ('#date-of-birth','#month-of-birth','#year-of-birth');
        prepareDateSelectBoxes ('#eff-date-of-birth','#eff-month-of-birth','#eff-year-of-birth');

        updateNumberOfDays('#date-of-birth','#month-of-birth', '#year-of-birth');
        updateNumberOfDays('#eff-date-of-birth','#eff-month-of-birth', '#eff-year-of-birth');

        $('#year-of-birth, #month-of-birth').on("change", function () {
            updateNumberOfDays('#date-of-birth','#month-of-birth', '#year-of-birth');
        });

        $('#eff-year-of-birth, #eff-month-of-birth').on("change", function () {
            updateNumberOfDays('#eff-date-of-birth','#eff-month-of-birth', '#eff-year-of-birth');
        });

        function updateNumberOfDays(dateID, monthID, yearID) {
            $(dateID).html('');
            month = $(monthID).val();
            year = $(yearID).val();
            days = daysInMonth(month, year);

            $(dateID).append($('<option selected="selected" disabled/>').html('Day'));
            for (i = 1; i < days + 1; i++) {
                $(dateID).append($('<option />').val(i).html(i));
            }
        }

        function daysInMonth(month, year) {
            return new Date(year, month, 0).getDate();
        }


        //Fill the Patient Form
        $.each(demographicRecord, function (name, val) {
            var $el = $(form).find('[name="' + name + '"]'),
                type = $el.attr('type');
            tagName = $el.prop('tagName');

            if (tagName == 'INPUT') {
                if (type == 'text' || type == 'email' || type == 'password' || type == 'hidden') {
                    $el.val(val);
                } else if (type == 'checkbox') {
                    $el.attr('checked', val);
                } else if (type == 'radio') {
                    $('input[value="' + val + '"]').attr('checked', 'checked');
                }
            } else if (tagName == 'SELECT') {
                $el.find('option[value="' + val + '"]').prop("selected", true);

            } else if (tagName == 'TEXTAREA') {
                $el.val(val);
            }
        });

        var effectiveDate = demographicRecord['effDate'];
        var splittedEffDate = effectiveDate.split("-");

        $(form).find('[name="effYearOfBirth"]').val(splittedEffDate[0]);
        $(form).find('[name="effMonthOfBirth"]').val(parseInt(splittedEffDate[1]));
        $(form).find('[name="effDateOfBirth"]').val(parseInt(splittedEffDate[2]));

        // Offer the first available date for an appointment.
        var earliestAvailableDate = moment(demographicRecord['appointmentStartDate']).format("YYYY-MM-DD HH:mm:ss");
        $(form).find('[name="appointmentStartDate"]').val(earliestAvailableDate);

        // Fill the appointment table
        updateAppointmentTable();

        $('#patient-form').on('submit', function (e) {
            e.preventDefault();
            requestAppointment();
        });

        var requestAppointment = function () {
            $("#floating-alert").hide();
            window.app.showSpinner('requestAppointment', $('#patient-form'));

            function padToLength(number, length) {
                if (number<=9) { number = ("0"+number).slice(-length); }
                return number;
            }

            var effYearOfBirth = $("#eff-year-of-birth").val();
            var effMonthOfBirth = padToLength($("#eff-month-of-birth").val(),2);
            var effDateOfBirth = padToLength($("#eff-date-of-birth").val(),2);

            var effDate = effYearOfBirth + "-" + effMonthOfBirth + "-" + effDateOfBirth;

            var lastName = demographicRecord["lastName"].substring(0, 24);
            var firstName = demographicRecord["firstName"].substring(0, 24);

            demographicRecord["userName"] = lastName + ', ' + firstName;
            demographicRecord["name"] = lastName + ', ' + firstName;

            demographicRecord["effDate"] = effDate;
            demographicRecord["hcType"] = $("#hc-type").val();
            demographicRecord["firstName"] = $("#first-name").val();
            demographicRecord["lastName"] = $("#last-name").val();
            demographicRecord["yearOfBirth"] = $("#year-of-birth").val();
            demographicRecord["monthOfBirth"] = $("#month-of-birth").val();
            demographicRecord["dateOfBirth"] = $("#date-of-birth").val();
            demographicRecord["phone"] = $("#phone").val();
            demographicRecord["phone2"] = $("#phone2").val();
            demographicRecord["email"] = $("#email").val();
            demographicRecord["address"] = $("#address").val();
            demographicRecord["city"] = $("#city").val();
            demographicRecord["province"] = $("#province").val();
            demographicRecord["postal"] = $("#postal-code").val();
            demographicRecord["officialLanguage"] = $("#official-language").val();
            demographicRecord["spokenLanguage"] = $("#spoken-language").val();
            demographicRecord["notes"] = $("#notes").val();
            demographicRecord["reason"] = $("#reason").val();
            demographicRecord["sex"] = $('input[name="sex"]:checked').val();
            demographicRecord["appointmentStartDate"] = $('input[name="appointmentStartDate"]').val();

            var phoneRegexObj = /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/;

            demographicRecord["phone"] = demographicRecord["phone"].replace(phoneRegexObj, "($1) $2-$3");
            demographicRecord["phone2"] = demographicRecord["phone2"].replace(phoneRegexObj, "($1) $2-$3");

            var postData = JSON.stringify(demographicRecord);

            window.app.postJSON({
                url: '/addAppointmentRecord',
                data: postData,
                completionHandler: function (result) {
                    $("#patient-form-container").html("");
                    $("#new-case-confirmation").show();
                    $("#appointment-info-confirmation").html(
                        "<strong>" + demographicRecord["firstName"] + " " + demographicRecord["lastName"] + "<br />" + demographicRecord["appointmentStartDate"] + "</strong>"
                    );
                },
                errorHandler: function (status, responseText, err) {
                    window.app.hideSpinner('requestAppointment');
                    if (status == 403)
                        $("#appointment-creation-error").show().text("Your session has expired. Please notify your coordinator and refresh the page.");
                    else if (status == 400)
                        $("#appointment-creation-error").show().text("There is an issue with some of the information you provided. Please review your entries and try again.");
                    else {
                        $("#floating-alert").show();
                        $("#floating-alert-text").html("<strong>Oops!</strong> Our appointment service seems to be down. Please try again in a few moments. (msg7)");
                        if (err) console.log(err.error.message);
                    }
                }
            });
        };

    }
});