$(document).ready(function() {

    window.app = new CLICKMD();
    window.app.getCoordinatorInformation();
    window.app.checkBrowser();

    $('#logout-menu-item').on('click', function(e) {
        e.preventDefault();

        $("main").html("")

        document.location.href='/signOut';
    });

})