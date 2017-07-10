
$(document).ready(function() {

// This is the part where jSignature is initialized.
	var $sigdiv1 = $("#signature1").jSignature({ 'UndoButton': true });
	//var export_plugins = $sigdiv.jSignature('listPlugins','export');


	$('#reset').bind('click', function(e){
		$sigdiv1.jSignature('reset');
	});

    $('#submit').bind('click', function(e){
        //console.log($sigdiv.jSignature('getData', 'base30'));
        var signatureData = $sigdiv1.jSignature('getData', 'default');
        var doc = new jsPDF('p','mm','letter');

//        doc.addPage()
        var waiverHTML = $("#signature1")
        doc.text( 15,40,"SIGNED By:" + "David Brooks" + "on November 1, 2016"  )

        doc.addImage(signatureData, 'PNG', 15, 80, 160, 40);
        var pdfData = doc.output("datauristring")
        doc.save( "test.pdf")

    })
});