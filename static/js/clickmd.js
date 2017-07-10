function CLICKMD() {

    // Private:

    var _self = this;
    var _spinners = {};

    this["coordinatorData"] = {};

    this.setMainMenuItems = function(){
        if( _self["coordinatorData"].admin == 'T' ) {
            $("#authorization-menu-item").show();
            $("#dashboard-menu-item").show();
            $('#doctors-on-call-menu-item').show();
            $('#manage-coordinators-menu-item').show();

            $("#authorization-button").show();
            $('#doctors-on-call-button').show();
            $("#manage-coordinators-button").show();

        }
        else {
            $("#authorization-menu-item").hide();
            $("#dashboard-menu-item").show();
            $('#doctors-on-call-menu-item').hide();
            $('#manage-coordinators-menu-item').hide();

            $("#authorization-button").hide();
            $('#doctors-on-call-button').hide();
            $("#manage-coordinators-button").hide();

        }

        $('#user-menu-item a.dropdown-toggle').html('<i class="fa fa-user"></i>&nbsp;&nbsp;Welcome, ' + _self.coordinatorData.firstName + '!&nbsp;&nbsp;<span class="caret"></span>');
        $("#user-logged-in-menu").show();
        $('#logo a').attr('href', '/dashboard');
        $('#home-button').attr('href', '/dashboard');

    }

    // Public:
    this.getCookie =  function(name, cookieString) {
        extractionPattern = new RegExp(".*" + name + "=\"(.*)\"" + ".*" );
        originalString = cookieString
        var cookieValue = cookieString.replace(extractionPattern, "$1")
        if( cookieValue == originalString)
            return ""
        else return cookieValue
    }
    this.coordinator_email = _self.getCookie( "_cmd-email_" , window.document.cookie );
    if( this.coordinator_email == "" ){
        if( document.location.href.indexOf("login") < 0 &&
            document.location.href.indexOf("register") < 0 &&
            document.location.href.indexOf("activate") < 0 &&
            document.location.href.indexOf("resetpassword") < 0 &&
            document.location.href.indexOf("splash") < 0 &&
            document.location.href.charAt( document.location.href.length -1 ) != '/'

        ) {
            $("main").html("")
            document.location.href = '/signOut';
        }

    }

    this.getCoordinatorInformation = function() {
        if (_self.coordinator_email.length <= 0){
           _self["coordinatorData"] = {};
            $("#user-not-logged-in-menu").show();
        }
        else{
            window.app.postJSON({
                url: "/getCoordinatorData",
                data: JSON.stringify({ "email": _self.coordinator_email }),
                completionHandler: function(result) {
                    _self["coordinatorData"] = result.data;
                    _self.setMainMenuItems()
                },
                errorHandler: function(code, msg, err) {
                    if (err && (code == 403 || code == 401))
                        window.location.assign('/signOut');
                    else {
                        $("#floating-alert").show();
                        $("#floating-alert-text").html("<strong>Oops!</strong> We weren't able to load your account information. Please reload the page.");
                        if (err) console.log(err.error.message);
                    }
                }
            });
        }
    }


    this.getJSON = function(options) {
        return $.ajax({
            type: 'GET',
            url: options.url,
            data: options.data,
            cache: false,
            headers: {
                'Accept': 'application/json'
            }
        }).done(function(data, textStatus, jqXHR) {
            if (options.completionHandler && typeof options.completionHandler == 'function') {
                options.completionHandler(data, textStatus, jqXHR);
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            if (options.errorHandler && typeof options.errorHandler == 'function') {
                options.errorHandler(jqXHR.status, jqXHR.responseText);
            }
        });
    }

    this.postJSON = function(options) {
        return $.ajax({
            type: 'POST',
            url: options.url,
            data: options.data,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        }).done(function(data, textStatus, jqXHR) {
            if (options.completionHandler && typeof options.completionHandler == 'function') {
                options.completionHandler(data, textStatus, jqXHR);
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            if (options.errorHandler && typeof options.errorHandler == 'function') {
                options.errorHandler(jqXHR.status, jqXHR.responseText, jqXHR.responseJSON);
            }
        });
    }

        this.spinners = function() {
        return _spinners;
    }

    this.deleteEntity = function(options) {
        return $.ajax({
            type: 'DELETE',
            url: options.url,
            headers: {
                'Accept': 'application/json'
            }
        }).done(function(data, textStatus, jqXHR) {
            if (options.completionHandler && typeof options.completionHandler == 'function') {
                options.completionHandler(data, textStatus, jqXHR);
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            if (options.errorHandler && typeof options.errorHandler == 'function') {
                options.errorHandler(jqXHR.status, jqXHR.responseText);
            }
        });
    }

    this.showSpinner = function(identifier, target, spinnerOptions, maskOptions) {
        // Prepare mask defaults:
        var maskDefaults = {
            showMask: true,
            className: 'spinner-mask',
            backgroundColor: 'rgba(255, 255, 255, 0.75)',
            zIndex: '2e9',
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%'
        };
        // Prepare the spinner and mask:
        if (!_self.spinners()[identifier]) {
            // Prepare the maks options:
            if (typeof spinnerOptions != 'object' || !spinnerOptions) {
                spinnerOptions = {
                    lines: 12, // The number of lines to draw
                    length: 12, // The length of each line
                    width: 3, // The line thickness
                    radius: 6, // The radius of the inner circle
                    corners: 1, // Corner roundness (0..1)
                    rotate: 0, // The rotation offset
                    direction: 1, // 1: clockwise, -1: counterclockwise
                    color: '#44565f', // #rgb or #rrggbb or array of colors
                    speed: 1, // Rounds per second
                    trail: 60, // Afterglow percentage
                    shadow: false, // Whether to render a shadow
                    hwaccel: false, // Whether to use hardware acceleration
                    className: 'spinner', // The CSS class to assign to the spinner
                    zIndex: 2e9, // The z-index (defaults to 2000000000)
                    top: '50%', // Top position relative to parent
                    left: '50%' // Left position relative to parent
                };
            }
            // Create the spinner:
            var spinner = new Spinner(spinnerOptions);
            // Prepare the mask options:
            if (typeof maskOptions == 'object' && maskOptions) {
                for (key in maskOptions) {
                    maskDefaults[key] = maskOptions[key];
                }
            }
            // Create the mask:
            var mask = document.createElement('div');
            mask.className = maskDefaults.className;
            mask.style.backgroundColor = maskDefaults.backgroundColor;
            mask.style.zIndex = maskDefaults.zIndex;
            mask.style.position = maskDefaults.position;
            mask.style.top = maskDefaults.top;
            mask.style.left = maskDefaults.left;
            mask.style.width = maskDefaults.width;
            mask.style.height = maskDefaults.height;
            // Store the spinner and mask:
            _self.spinners()[identifier] = {
                spinner: spinner,
                mask: mask
            };
        }

        // Show the spinner:
        if (maskDefaults.showMask) {
            // Append the mask to the target and show the spinner in the mask:
            _self.spinners()[identifier].spinner.spin(_self.spinners()[identifier].mask);
            $(target).append(_self.spinners()[identifier].mask);
        } else {
            // Show the spinner in the target:
            _self.spinners()[identifier].spinner.spin($(target).get(0));
        }
    }

    this.hideSpinner = function(identifier) {
        if (_spinners[identifier]) {
            _spinners[identifier].spinner.stop();
            $(_spinners[identifier].mask).remove();
        }
    }

    this.destroySpinner = function(identifier) {
        _self.hideSpinner(identifier);
        _spinners[identifier] = null;
    }

    // Reset Form

    this.resetForm = function($form) {
        $form.find('input:text, input:password, input:file, select, textarea').val('');
        $form.find('input:radio, input:checkbox').removeAttr('checked').removeAttr('selected');
        $form.find('span.form-error').parent().removeClass('has-error');
        $form.find('input.valid, select.valid, textarea.valid').parent('div.has-success').removeClass('has-success');
        $form.find('input.valid, select.valid, textarea.valid').removeClass('valid');
        $form.find('span.form-error').parent().find('input, select, textarea').removeClass('error').removeAttr( 'style' );;
        $form.find('span.form-error').remove();
    }

     // Alerts:

    this.prepareMessageText = function(title, message) {
        var messageText = '';
        if (title && title.length > 0) {
            messageText += title;
            if (message && message.length > 0) {
                messageText += ': ';
            }
        }
        if (message && message.length > 0) {
            messageText += message;
        }
        return messageText;
    }

    this.alert = function(title, message, alertType, parentContainer) {
        // Set the default alert type:
        var alertTypes = ['info', 'success', 'warning', 'danger'];
        if (alertTypes.indexOf(alertType) == -1) {
            alertType = 'info';
        }

        // Remove existing alert classes:
        for (var i = 0; i < alertTypes.length; i++) {
            $(parentContainer).find('.message-container > .message-content').removeClass('alert-' + alertTypes[i]);
        }
        // Add the new alert class:
        $(parentContainer).find('.message-container > .message-content').addClass('alert-' + alertType);
        // Insert the message:
        $(parentContainer).find('.message-container > .message-content > .message-text').text(_self.prepareMessageText(title, message));
        $(parentContainer).find('.message-container').slideDown('fast');
    }

    this.handleError = function(message, subMessage, parentContainer) {
        if (subMessage && subMessage.length > 0) {
            message += ' (' + subMessage + ')';
        }
        _self.alert('Error', message, 'danger', parentContainer);
    }

    this.messageFromErrorResponse = function(responseText) {
        try {
            var responseObj = JSON.parse(responseText);
            if (responseObj.message) {
                return responseObj.message;
            }
            return '';
        } catch(e) {
            return '';
        }
    }

    this.checkBrowser = function() {
        if (Modernizr.canvas && Modernizr.svg && Modernizr.checked && Modernizr.svgasimg) {
            $('#browser-warning').hide(); // supported
        } else {
            $('#browser-warning').show();// not-supported
        }
    }
}