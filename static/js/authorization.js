var coordinators = []

var originalBody = {};
var getUnauthorizedCoordinatorsTimer = null;

function authorizeCoordinator( coordinatorId ) {
    window.app.postJSON({
        url: "/setAuthorizedCoordinator",
        data: JSON.stringify({ "coordinatorId" : coordinatorId }),
        completionHandler: function(result) {

            window.app.postJSON({
                url: "/getUnauthorizedCoordinators",
                data: JSON.stringify({  }),
                completionHandler: function(result) {
                    coordinators = result.data
                    dataespRepeatDigest()
                    window.app.setMainMenuItems()

                },
                errorHandler: function(code, msg) {
                    console.log(msg);
                }
            });


        },
        errorHandler: function(code, msg) {
            console.log(msg);
        }
    });

}


function dataespRepeatDigest(){
    // save the original content,
    // otherwise, after replacing DOM elements this process couldn't be repeated
    $("main").replaceWith(originalBody.clone());


    // look for every dataesp-repeat class
    $("[dataesp-repeat]").each( function(index) {


        // the value of dataesp-repeat is the array to repeat and the name to give each element
        // dataesp-repeat="c in coordinators"
        var attrValue = $(this).attr("dataesp-repeat")

        var inPosition = attrValue.indexOf( " in " )
        // make sure the syntax of the attribute is correct
        if( inPosition > 0 ) {

            var aliasName = $.trim(attrValue.substring(0, inPosition))
            var collectionName = $.trim(attrValue.substring(inPosition + 3))
            var repeatingContent = $(this).html()
            var thisElement = $(this).parent().html()
            var firstClosingBracket = thisElement.indexOf( ">" )
            // again, check for a syntax error
            // the opening tag must be repeated, with /tag at the end
            if( firstClosingBracket > 1 ) {
                var tagName = $(this).prop("tagName");
                thisElement = thisElement.substring(0,firstClosingBracket+1 )
                // the parent element is the one that will contain the repeating content
                // we will use jquery append to add the repeating content
                var parentElement = $(this).parent();

                // remove the template for the repeating content
                $(this).remove()

                // convert <% to html entities to make it consistent for all variables
                // sometimes they are already converted
                repeatingContent = repeatingContent.replace("<%","&lt;%")
                repeatingContent = repeatingContent.replace("%>","%&gt;")
                var variableArray = repeatingContent.match(/(\&lt;%.*%&gt;)/g)
                var collectionToIterate = eval(collectionName)

                for (var collectionIndex = 0; collectionIndex < collectionToIterate.length; collectionIndex++) {
                    var newContent = thisElement

                    var aliasingString = "var " + aliasName + " = " + collectionName + "[collectionIndex]";
                    eval(aliasingString)
                    newContent += repeatingContent;

                    // go in and replace all the variables
                    for (var v = 0; v < variableArray.length; v++) {
                        var variableName = variableArray[v]
                        // use regex to replace the variable block with the actual value in the collection
                        // i.e. replace <% c.name %> with eval(variableName)
                        variableName = variableName.replace(/\&lt;%/g, "")
                        variableName = variableName.replace(/%&gt;/g, "")
                        variableName = $.trim(variableName)
                        var re = new RegExp(variableArray[v], 'g');
                        newContent = newContent.replace(re, eval(variableName))

                    }
                    // close the repeating content tag
                    newContent += "</" + tagName + ">"
                    // append the new content to the parent element
                    parentElement.append(newContent)
                }
            }

        }

    })


}

function getUnauthorizedCoordinators(){

    // stop the timer, then start it after the endpoint has returned results
    // prevents any possibility of piling up requests
    if( getUnauthorizedCoordinatorsTimer != null)
        clearInterval(getUnauthorizedCoordinatorsTimer);

    window.app.postJSON({
        url: "/getUnauthorizedCoordinators",
        data: JSON.stringify({  }),
        completionHandler: function(result) {
            coordinators = result.data
            // we know content has changed, so explicitly call out own digest cycle
            dataespRepeatDigest()
            window.app.setMainMenuItems()

            getUnauthorizedCoordinatorsTimer = setTimeout(getUnauthorizedCoordinators, 5000);

        },
        errorHandler: function(code, msg) {
            console.log(msg);
            getUnauthorizedCoordinatorsTimer = setTimeout(getUnauthorizedCoordinators, 5000);

        }
    });

}

$(document).ready(function() {


    originalBody = $("main").clone()
    getUnauthorizedCoordinatorsTimer = setTimeout(getUnauthorizedCoordinators, 100);



});
