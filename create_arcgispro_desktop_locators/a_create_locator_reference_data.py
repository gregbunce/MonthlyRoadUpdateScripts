import arcpy, shutil, os

#: Notes: verify these variables: 
    # use arcgispro-py3
    # sgidAddressPoints (using local copy when at home)


# variables
# sgidAddressPoints = "Database Connections\\internal@SGID@internal.agrc.utah.gov.sde\\SGID.LOCATION.AddressPoints"
sgidAddressPoints = "C:\\Users\\gbunce\\Documents\\projects\\SGID\\local_sgid_data\\SGID_2022_11_14.gdb\\AddressPoints" #: use local copy when at home
rebuildLocators_Folder = 'C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators'
previousRebuildLocators_Folder = 'C:\\Users\\gbunce\\Documents\\projects\\RebuildAddressLocators\\_previousRebuild'
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