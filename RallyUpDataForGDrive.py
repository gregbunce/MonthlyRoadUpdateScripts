import arcpy, os, shutil, datetime, zipfile, glob

#: Notes before running: verify that these variables are pointing to the correct data (ie: VPN vs at work)
mmp_network = "C:\\Users\\gbunce\\Documents\\projects\\MultimodalNetwork\\MM_NetworkDataset_06142022.gdb"
statewide_road_network = "C:\\Users\\gbunce\\Documents\\projects\\NetworkDataset\\RecentBuilds\\2022_6_14\\UtahRoadsNetworkAnalysis.gdb"
roadGrinderDatabase = "C:\\Temp\\RoadGrinder.gdb" # this path and file name should be stable, not needing to be repointed
ng911Database = "C:\\Temp\\NG911GIS_Schema.gdb" # this path and file name should be stable, not needing to be repointed
# sgidRoads (roads are now accessed via open data so this process is no longer needed)


#### BEGIN >>> Zip Shapefile function ####
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
#### Zip Shapefile function  <<< END ####

#### BEGIN >>> Zip File Geodatabase function ####
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
#### Zip File Geodatabase function <<< END ####


#### BEGIN >>> Zip Locator Packages function ####
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
#### Zip Locator Packages function <<< END ####

#### __Main__ ####
####: Create a folder based on the date (ie: Year_Month_Day = 2018_4_16)
now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day
folder_name = str(year) + "_" + str(month) + "_" + str(day)
#: create the folder
directory = "C:\\Users\\gbunce\\Documents\\projects\\DataForGDrive\\" + folder_name
if not os.path.exists(directory):
    print "Creating Directory: " + str(directory) + " ..."
    os.makedirs(directory)
else:
    print "Directory: " + str(directory) + " exists."
# set this folder as the work env
arcpy.env.workspace = directory


####: Fetch the data and bring it to C:\\Users\\gbunce\\Documents\\projects\\DataForGDrive\\ ####

##: RoadGrinder.gdb (i'm no longer moving the file into the DataForGDrive folder, now leaving it where it is and moving the zipped file)
#roadGrinderDatabase = "G:/Team Drives/AGRC Projects/Locators/RoadGrinder.gdb"
# roadGrinderDatabase = "C:/Temp/RoadGrinder.gdb"
# print "Copying RoadGrinder.gdb from c:/temp folder to the DataForGDrive folder ..."
# arcpy.Copy_management(roadGrinderDatabase, "RoadGrinder.gdb")

#: Get sgid roads data (roads are now accessed via open data so this process is no longer needed)
# sgidRoads = "Database Connections\\internal@SGID@internal.agrc.utah.gov.sde\\SGID.TRANSPORTATION.Roads" #: use a local copy when connected to the VPN
# sgidRoads = "C:\Users\\gbunce\\Documents\\projects\\SGID\\local_sgid_data\\SGID_2020_10_09.gdb\\Roads"

##: Roads.gdb (roads are now accessed via open data so this process is no longer needed)
#print "Importing SGID.Roads into Road.gdb ..."
# arcpy.CreateFileGDB_management(directory, "Roads.gdb")
# arcpy.FeatureClassToFeatureClass_conversion(sgidRoads, "Roads.gdb", "Roads")

#: Roads.shp (roads are now accessed via open data so this process is no longer needed)
#print "Importing SGID.Roads into Road.shp ..."
# arcpy.FeatureClassToShapefile_conversion(sgidRoads, directory)

##: UtahNG911GIS.gdb (i'm no longer moving the file into the DataForGDrive folder, now leaving it where it is and moving the zipped file)
#ng911Database = "\\\\itwfpcap2\\AGRC\\agrc\\data\\ng911\\UtahNG911GIS.gdb"
# ng911Database = "C:\Users\\gbunce\\Documents\\projects\\NG911_Database\\LatestDB\\UtahNG911GIS.gdb"
# print "Copying UtahNG911GIS.gdb from local ng911 folder to the DataForGDrive folder ..."
# arcpy.Copy_management(ng911Database, "UtahNG911GIS.gdb")

# ##: MM_NetworkDataset_date.gdb (i'm not longer moving the file into the DataForGDrive folder, now leaving it where it is and moving the zipped file)
# mmp_network = "C:\\Users\\gbunce\\Documents\\projects\\MultimodalNetwork\\MM_NetworkDataset_01072021.gdb"
# print "Copying MM_Network Dataset to the DataForGDrive folder ..."
# arcpy.Copy_management(mmp_network, "MM_NetworkDataset.gdb")

# ##: UtahRoadsNetworkAnalysis.gdb (i'm not longer moving the file into the DataForGDrive folder, now leaving it where it is and moving the zipped file)
# statewide_road_network = "C:\\Users\\gbunce\\Documents\\projects\\NetworkDataset\\RecentBuilds\\2021_1_7\\UtahRoadsNetworkAnalysis.gdb"
# print "Copying UtahRoadsNetwork dataset to the DataForGDrive folder ..."
# arcpy.Copy_management(statewide_road_network, "UtahRoadsNetworkAnalysis.gdb")

##: AGRC_AddressPointLocator.gcpk
addressPntLocatorPackage = "C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators\\AGRC_AddressPointLocator.gcpk"
print "Copying AGRC_AddressPointLocator.gcpk from C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators to the C:\\Users\\gbunce\\Documents\\projects\\DataForGDrive folder ..."
arcpy.Copy_management(addressPntLocatorPackage, "AGRC_AddressPointLocator.gcpk")

##: AGRC_RoadsLocator.gcpk
roadsLocatorPackage = "C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators\\AGRC_RoadsLocator.gcpk"
print "Copying AGRC_RoadsLocator.gcpk from C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators to the C:\\Users\\gbunce\\Documents\\projects\\DataForGDrive folder ..."
arcpy.Copy_management(roadsLocatorPackage, "AGRC_RoadsLocator.gcpk")

##: AGRC_CompositeLocator.gcpk
compositeLocatorPackage = "C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators\\AGRC_CompositeLocator.gcpk"
print "Copying AGRC_CompositeLocator.gcpk from C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators to the C:\\Users\\gbunce\\Documents\\projects\\DataForGDrive folder ..."
arcpy.Copy_management(compositeLocatorPackage, "AGRC_CompositeLocator.gcpk")

#: now compress the files (zip them up)

#: zip the shapefiles
# ZipShp(directory + "/Roads.shp", False)

##: zip the geodatabases
# ZipFileGeodatabase(directory + "/RoadGrinder.gdb", directory + "/RoadGrinder_gdb.zip")
# ZipFileGeodatabase(directory + "/UtahNG911GIS.gdb", directory + "/UtahNG911GIS_gdb.zip")
ZipFileGeodatabase(roadGrinderDatabase, directory + "/RoadGrinder_gdb.zip")
#ZipFileGeodatabase(ng911Database, directory + "/UtahNG911GIS_gdb.zip")
ZipFileGeodatabase(mmp_network, directory + "/MM_NetworkDataset_gdb.zip")
ZipFileGeodatabase(statewide_road_network, directory + "/UtahRoadsNetworkAnalysis_gdb.zip")
#ZipFileGeodatabase(directory + "/Roads.gdb", directory + "/Roads_gdb.zip")

##: zip the locator packages
ZipLocatorPackages(directory, "AGRC_AddressLocatorsPackage")

print "Done!"
