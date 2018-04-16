import arcpy, os, zipfile, glob

#### Zip Shapefile ####
def ZipShp (inShp, Delete = True):
 
    """
    Creates a zip file containing the input shapefile
    inputs -
    inShp: Full path to shapefile to be zipped
    Delete: Set to True to delete shapefile files after zip
    """
     
    #List of shapefile file extensions
    extensions = [".shp",
                  ".shx",
                  ".dbf",
                  ".sbn",
                  ".sbx",
                  ".fbn",
                  ".fbx",
                  ".ain",
                  ".aih",
                  ".atx",
                  ".ixs",
                  ".mxs",
                  ".prj",
                  ".xml",
                  ".cpg",
                  ".shp.xml"]
 
    #Directory of shapefile
    inLocation = arcpy.Describe (inShp).path
    #Base name of shapefile
    inName = arcpy.Describe (inShp).baseName
    #Create zipfile name
    zipfl = os.path.join (inLocation, inName + "_shp.zip")
    #Create zipfile object
    ZIP = zipfile.ZipFile (zipfl, "w")
     
    #Iterate files in shapefile directory
    for fl in os.listdir (inLocation):
        #Iterate extensions
        for extension in extensions:
            #Check if file is shapefile file
            if fl == inName + extension:
                #Get full path of file
                inFile = os.path.join (inLocation, fl)
                #Add file to zipfile
                ZIP.write (inFile, fl)
                break
 
    #Delete shapefile if indicated
    if Delete == True:
        arcpy.Delete_management (inShp)
 
    #Close zipfile object
    ZIP.close()
 
    #Return zipfile full path
    return zipfl

#### Zip File Geodatabase ####
def ZipFileGeodatabase(inFileGeodatabase, newZipFN):
   if not (os.path.exists(inFileGeodatabase)):
      return False

   if (os.path.exists(newZipFN)):
      os.remove(newZipFN)

   zipobj = zipfile.ZipFile(newZipFN,'w')

   for infile in glob.glob(inFileGeodatabase+"/*"):
      zipobj.write(infile, os.path.basename(inFileGeodatabase)+"/"+os.path.basename(infile), zipfile.ZIP_DEFLATED)
      print ("Zipping: "+infile)

   zipobj.close()

   return True

#### Zip Locator Packages ####
def ZipLocatorPackages (folderLocation, outputName):
     
    #List of file extensions
    extensions = [".gcpk"]

    # Create zipfile name
    zipfl = os.path.join (folderLocation, outputName + "_gcpk.zip")
    # Create zipfile object
    ZIP = zipfile.ZipFile (zipfl, "w")
     
    # Iterate files in directory
    for fl in os.listdir (folderLocation):
        # Iterate extensions
        for extension in extensions:
            # Check if file has correct extension
            if fl.endswith(extension):
                # Get full path of file
                packageName = os.path.join (folderLocation, fl)
                # Add file to zipfile
                ZIP.write (packageName, fl)
                break
 
    # Close zipfile object
    ZIP.close()
 
    # Return zipfile full path
    return zipfl