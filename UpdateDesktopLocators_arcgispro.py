import arcpy, shutil, os

#: Notes: verify these variables: 
    # use arcgispro-py3
    # sgidAddressPoints (using local copy when at home)


# variables
# sgidAddressPoints = "Database Connections\\internal@SGID@internal.agrc.utah.gov.sde\\SGID.LOCATION.AddressPoints"
sgidAddressPoints = "C:\\Users\\gbunce\\Documents\\projects\\SGID\\local_sgid_data\\SGID_2022_8_4.gdb\\AddressPoints" #: use local copy when at home

rebuildLocators_Folder = 'C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators'
previousRebuildLocators_Folder = 'C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators\\_previousRebuild'
googledrive_locator_folder = 'G:\\Shared drives\\AGRC Projects\\Locators'
previous_googledrive_locator_folder = 'G:\\Shared drives\\AGRC Projects\\Locators\\_previousRebuild'
addressPointLocator = "ugrc_address_point_locator"
roadsLocator = "ugrc_roads_locator"
compositeLocator = "ugrc_composite_locator"
arcpy.env.workspace = "C:/Users/gbunce/Documents/projects/RebuildAddressLocators"

#### Move all existing files in rebuild folder to the backup folder. ####
# delete all files in the backup folder
print("Deleting the local _previousRebuild folder and all the files")
shutil.rmtree(previousRebuildLocators_Folder)
# create the folder again
print("Recreating the local _previousRebuild folder")
os.makedirs(previousRebuildLocators_Folder)

files = os.listdir(rebuildLocators_Folder)
print("Moving existing files in the rebuild folder to the _previousRebuild folder...")
for f in files:
    shutil.move(rebuildLocators_Folder+ "/" + f, previousRebuildLocators_Folder)

#### Move roadgrinder from roadgrinder-output folder to rebuild folder ####
roadGrinderOutput = "C:/temp/RoadGrinder.gdb"
print("Copying RoadGrinder.gdb from C:/temp to the rebuild folder...")
arcpy.Copy_management(roadGrinderOutput, rebuildLocators_Folder + "/RoadGrinder.gdb")

#### Import the address point from SGID into the roadgrinder database. ####
print("Importing SGID.AddressPoints into RoadGrinder.gdb in local rebuild folder...")
arcpy.FeatureClassToFeatureClass_conversion(sgidAddressPoints, rebuildLocators_Folder + "/RoadGrinder.gdb", "SgidAddrPnts")

#### Copy the three locators from google drive to the local rebuild folder. ####
print("Copying the 3 locators from HNAS to the rebuild folder...")
arcpy.Copy_management(googledrive_locator_folder + "/" + addressPointLocator, rebuildLocators_Folder + "/" + addressPointLocator)
arcpy.Copy_management(googledrive_locator_folder + "/" + roadsLocator, rebuildLocators_Folder + "/" + roadsLocator)
arcpy.Copy_management(googledrive_locator_folder + "/" + compositeLocator, rebuildLocators_Folder + "/" + compositeLocator)

#### Rebuild the locators in the rebuild folder. ####
print("start rebuilding UGRC_AddressPointLocator in rebuild folder...")
arcpy.geocoding.RebuildAddressLocator(addressPointLocator)
print("done rebuilding UGRC_AddressPointLocator in rebuild folder")
print("start rebuilding UGRC_RoadsLocator...")
arcpy.geocoding.RebuildAddressLocator(roadsLocator)
print("done rebuilding UGRC_RoadsLocator in rebuild folder")
print("start rebuilding UGRC_CompositeLocator...")
arcpy.geocoding.RebuildAddressLocator(compositeLocator)
print("done rebuilding UGRC_CompositeLocator")

#### Create the locator packages ####
print("Creating address locator packages....")
arcpy.PackageLocator_management(addressPointLocator, addressPointLocator + '.gcpk', "", "#","UGRC AddressPoint Locator","UGRC; AddressPointAddressLocator")
arcpy.PackageLocator_management(roadsLocator, roadsLocator + '.gcpk', "", "#","UGRC Roads Locator","UGRC; RoadsAddressLocator")
arcpy.PackageLocator_management(compositeLocator, compositeLocator + '.gcpk', "", "#","UGRC Composite Locator","UGRC; CompositeAddressLocator")


##################################################################################################
#### move the old locators, packages, and gdb to the _previous folder on hnas ####
# delete all files in the backup folder
print("Deleting the folder and all the files >>> G:/Shared drives/AGRC Projects/Locators/PreviousLocators ...")
shutil.rmtree(previous_googledrive_locator_folder)
# create the folder again
print("Recreating the empty directory G:/Shared drives/AGRC Projects/Locators/PreviousLocators ...")
os.makedirs(previous_googledrive_locator_folder)

# copy the rebuilt locators, locator packages, and new roadgrinder.gdb to hnas
files = os.listdir(googledrive_locator_folder)
print("Moving existing files in G:/Shared drives/AGRC Projects/Locators to G:/Shared drives/AGRC Projects/Locators/PreviousLocators ...")
for f in files:
    shutil.move(googledrive_locator_folder+ "/" + f, previous_googledrive_locator_folder)

### Copy contents from rebuild folders to G:/Shared drives/AGRC Projects/Locators
print("Copying files from D:/Rebuild Address Locators to G:/Shared drives/AGRC Projects/Locators ...")
arcpy.Copy_management("/RoadGrinder.gdb", googledrive_locator_folder + "/RoadGrinder.gdb")
arcpy.Copy_management(addressPointLocator, googledrive_locator_folder + "/" + addressPointLocator)
arcpy.Copy_management(roadsLocator, googledrive_locator_folder + "/" + roadsLocator)
arcpy.Copy_management(compositeLocator , googledrive_locator_folder + "/" + compositeLocator)
arcpy.Copy_management(addressPointLocator + '.gcpk', googledrive_locator_folder + "/" + addressPointLocator + '.gcpk')
arcpy.Copy_management(roadsLocator + '.gcpk', googledrive_locator_folder + "/" + roadsLocator + '.gcpk')
arcpy.Copy_management(compositeLocator + '.gcpk', googledrive_locator_folder + "/" + compositeLocator + '.gcpk')

print("Done!")