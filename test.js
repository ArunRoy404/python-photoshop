// Replace SmartObjects Content based on specific paths
// Target: Photoshop

main();

function main() {
    // 1. CONFIGURATION - Using your specific paths
    var psdPath = "C:/Users/ROY/Desktop/python-photoshop/psdFiles/mug.psd";
    var imagesDir = "C:/Users/ROY/Desktop/python-photoshop/images";
    var outputDir = "C:/Users/ROY/Desktop/python-photoshop/output";
    var targetLayerName = "front_surface"; 

    // 2. OPEN THE TEMPLATE
    var fileRef = new File(psdPath);
    if (!fileRef.exists) {
        alert("Error: Template PSD not found at " + psdPath);
        return;
    }
    var myDocument = app.open(fileRef);

    // 3. PREPARE OUTPUT FOLDER
    var outFolder = new Folder(outputDir);
    if (!outFolder.exists) outFolder.create();

    // 4. FIND THE SMART OBJECT LAYER BY NAME
    var theLayer;
    try {
        theLayer = myDocument.layers.getByName(targetLayerName);
    } catch (e) {
        alert("Error: Could not find layer named '" + targetLayerName + "'");
        myDocument.close(SaveOptions.DONOTSAVECHANGES);
        return;
    }

    if (theLayer.kind != LayerKind.SMARTOBJECT) {
        alert("Error: Layer '" + targetLayerName + "' is not a Smart Object.");
        return;
    }

    // 5. GET IMAGES FROM DIRECTORY
    var imgFolder = new Folder(imagesDir);
    var theFiles = imgFolder.getFiles(/\.(jpg|tif|psd|png)$/i);

    if (theFiles.length == 0) {
        alert("No images found in: " + imagesDir);
        return;
    }

    // 6. SAVE OPTIONS
    var psdOpts = new PhotoshopSaveOptions();
    psdOpts.embedColorProfile = true;
    psdOpts.layers = true;

    // 7. LOOP AND REPLACE
    for (var m = 0; m < theFiles.length; m++) {
        // Replace SmartObject
        replaceContents(theFiles[m], theLayer);

        // Define output name based on image name
        var imgName = theFiles[m].name.match(/(.*)\.[^\.]+$/)[1];
        var saveFile = new File(outputDir + "/" + imgName + "_mug.psd");

        myDocument.saveAs(saveFile, psdOpts, true);
    }

    alert("Done! Processed " + theFiles.length + " images.");
}

// Function to replace Smart Object contents
function replaceContents(newFile, theSO) {
    app.activeDocument.activeLayer = theSO;
    var idplacedLayerReplaceContents = stringIDToTypeID("placedLayerReplaceContents");
    var desc3 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    desc3.putPath(idnull, new File(newFile));
    var idPgNm = charIDToTypeID("PgNm");
    desc3.putInteger(idPgNm, 1);
    executeAction(idplacedLayerReplaceContents, desc3, DialogModes.NO);
}