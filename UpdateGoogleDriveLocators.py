import arcpy, shutil, os

# variables
rebuildLocators_Folder = 'C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators'
previousRebuildLocators_Folder = 'C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators\\_previousRebuild'
#hnasLocators_Folder = 'K:/AGRC Projects/Locators'
hnasLocators_Folder = 'G:\\Shared drives\\AGRC Projects\\Locators'
#previousHnasLocators_Folder = 'K:/AGRC Projects/Locators/PreviousLocators'
previousHnasLocators_Folder = 'G:\\Shared drives\\AGRC Projects\\Locators\\_previousRebuild'
sgidAddressPoints = "Database Connections\\internal@SGID@internal.agrc.utah.gov.sde\\SGID.LOCATION.AddressPoints"
addressPointLocator = "AGRC_AddressPointLocator"
roadsLocator = "AGRC_RoadsLocator"
compositeLocator = "AGRC_CompositeLocator"
arcpy.env.workspace = rebuildLocators_Folder

#### Move all existing files in rebuild folder to the backup folder. ####
# delete all files in the backup folder
print "Deleting the folder and all the files >>> C:\Users\gbunce\Documents\projects\RebuildAddressLocators\_previousRebuild..."
shutil.rmtree(previousRebuildLocators_Folder)
# create the folder again
print "Recreating the empty directory C:\Users\gbunce\Documents\projects\RebuildAddressLocators\_previousRebuild..."
os.makedirs(previousRebuildLocators_Folder)

files = os.listdir(rebuildLocators_Folder)
print "Moving existing files in the rebuild folder to the _previousRebuild folder..."
for f in files:
    shutil.move(rebuildLocators_Folder+ "/" + f, previousRebuildLocators_Folder)

#### Move roadgrinder from roadgrinder-output folder to rebuild folder ####
roadGrinderOutput = "C:/temp/RoadGrinder.gdb"
print "Copying RoadGrinder.gdb from C:/temp to the rebuild folder..."
arcpy.Copy_management(roadGrinderOutput, rebuildLocators_Folder + "/RoadGrinder.gdb")

#### Import the address point from SGID into the roadgrinder database. ####
print "Importing SGID.AddressPoints into RoadGrinder.gdb in local rebuild folder..."
arcpy.FeatureClassToFeatureClass_conversion(sgidAddressPoints, rebuildLocators_Folder + "/RoadGrinder.gdb", "SgidAddrPnts")

#### Copy the three locators from hnas to the rebuild folder. ####
print "Copying the 3 locators from HNAS to the rebuild folder..."
arcpy.Copy_management(hnasLocators_Folder + "/" + addressPointLocator, rebuildLocators_Folder + "/" + addressPointLocator)
arcpy.Copy_management(hnasLocators_Folder + "/" + roadsLocator, rebuildLocators_Folder + "/" + roadsLocator)
arcpy.Copy_management(hnasLocators_Folder + "/" + compositeLocator, rebuildLocators_Folder + "/" + compositeLocator)

#### Rebuild the locators in the rebuild folder. ####
print "start rebuilding AGRC_AddressPointLocator in rebuild folder..."
arcpy.RebuildAddressLocator_geocoding(rebuildLocators_Folder + "/" + addressPointLocator)
print "done rebuilding AGRC_AddressPointLocator in rebuild folder"
print "start rebuilding AGRC_RoadsLocator..."
arcpy.RebuildAddressLocator_geocoding(rebuildLocators_Folder + "/" + roadsLocator)
print "done rebuilding AGRC_RoadsLocator in rebuild folder"
print "start rebuilding AGRC_CompositeLocator..."
arcpy.RebuildAddressLocator_geocoding(rebuildLocators_Folder + "/" + compositeLocator)
print "done rebuilding AGRC_CompositeLocator"

#### Create the locator packages ####
print "Creating address locator packages...."
arcpy.PackageLocator_geocoding(addressPointLocator, addressPointLocator + '.gcpk', "COPY_ARCSDE", "#","AGRC AddressPoint Locator","AGRC; AddressPointAddressLocator")
arcpy.PackageLocator_geocoding(roadsLocator, roadsLocator + '.gcpk', "COPY_ARCSDE", "#","AGRC Roads Locator","AGRC; RoadsAddressLocator")
arcpy.PackageLocator_geocoding(compositeLocator, compositeLocator + '.gcpk', "COPY_ARCSDE", "#","AGRC Composite Locator","AGRC; CompositeAddressLocator")


##################################################################################################
#### move the old locators, packages, and gdb to the _previous folder on hnas ####
# delete all files in the backup folder
print "Deleting the folder and all the files >>> G:/Shared drives/AGRC Projects/Locators/PreviousLocators ..."
shutil.rmtree(previousHnasLocators_Folder)
# create the folder again
print "Recreating the empty directory G:/Shared drives/AGRC Projects/Locators/PreviousLocators ..."
os.makedirs(previousHnasLocators_Folder)

# copy the rebuilt locators, locator packages, and new roadgrinder.gdb to hnas
files = os.listdir(hnasLocators_Folder)
print "Moving existing files in G:/Shared drives/AGRC Projects/Locators to G:/Shared drives/AGRC Projects/Locators/PreviousLocators ..."
for f in files:
    shutil.move(hnasLocators_Folder+ "/" + f, previousHnasLocators_Folder)

### Copy contents from rebuild folders to G:/Shared drives/AGRC Projects/Locators
print "Copying files from D:/Rebuild Address Locators to G:/Shared drives/AGRC Projects/Locators ..."
arcpy.Copy_management("/RoadGrinder.gdb", hnasLocators_Folder + "/RoadGrinder.gdb")
arcpy.Copy_management(addressPointLocator, hnasLocators_Folder + "/" + addressPointLocator)
arcpy.Copy_management(roadsLocator, hnasLocators_Folder + "/" + roadsLocator)
arcpy.Copy_management(compositeLocator , hnasLocators_Folder + "/" + compositeLocator)
arcpy.Copy_management(addressPointLocator + '.gcpk', hnasLocators_Folder + "/" + addressPointLocator + '.gcpk')
arcpy.Copy_management(roadsLocator + '.gcpk', hnasLocators_Folder + "/" + roadsLocator + '.gcpk')
arcpy.Copy_management(compositeLocator + '.gcpk', hnasLocators_Folder + "/" + compositeLocator + '.gcpk')

print "Done!"