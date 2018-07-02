import arcpy, os, datetime

# this runs as on a weekly scheduled task on my machine (for now - then maybe forklift after testing)

def DeletePreviousBoundaries():
    print("Deleting _Prev boundaries...")
    datasets = arcpy.ListDatasets(feature_type='feature')
    datasets = [''] + datasets if datasets is not None else []

    for ds in datasets:
        for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
            #path = os.path.join(arcpy.env.workspace, ds, fc)
            if "_Prev" in str(fc):
                arcpy.Delete_management(fc)
                


def RenameExistingDatasets():
    print("Renaming existing boundaries to append _Prev...")
    datasets = arcpy.ListDatasets(feature_type='feature')
    datasets = [''] + datasets if datasets is not None else []

    for ds in datasets:
        for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
            #path = os.path.join(arcpy.env.workspace, ds, fc)
            arcpy.Rename_management(fc, fc + "_Prev")


def ImportSGIDBoundaries():
    print("Importing SGID boundaries...")
    for feature_class in feature_class_list:
        if feature_class == "AddressSystemQuadrants":
            arcpy.FeatureClassToFeatureClass_conversion(sgid_connection + "LOCATION." + feature_class, arcpy.env.workspace, feature_class)
        else:
            arcpy.FeatureClassToFeatureClass_conversion(sgid_connection + "BOUNDARIES." + feature_class, arcpy.env.workspace, feature_class)


def RunSymmetricalDifference():
    print("Running symmetrical difference to look for changes...")
    for feature_class in feature_class_list:
        arcpy.SymDiff_analysis(feature_class + "_Prev", feature_class, str(changes_fgdb) + "/SymDiff_" + str(feature_class), "ALL")


def GetBoundaryUpdates_Count():
    # switch workspace for this function (.ListDatasets)
    arcpy.env.workspace = str(changes_fgdb)

    # loop through the feature classes and get count if feature class name conatins SymDiff_
    for fc in arcpy.ListFeatureClasses():
        count = arcpy.GetCount_management(fc)
        log_file.write(str(fc) + " Change Count: " + str(count) + "\n")
        print(str(fc) + " Change Count: " + str(count))


# Main function
if __name__ == "__main__":
    try:
        # get date variables
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        min = now.minute
        formatted_date = str(year) + "_" + str(month) + "_" + str(day)
        formatted_date_with_time = str(year) + "mon" + str(month) + "d" + str(day) + "h" + str(hour) + "min" + str(min)

        # data paths
        arcpy.env.workspace = 'D:/BoundaryChanges/Boundaries.gdb'
        boundaryFGDB = 'Boundaries.gdb'
        changesFGDB = 'Changes_' + formatted_date + '.gdb'
        projectFolder = 'D:/BoundaryChanges'
        sgid_connection = 'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.'

        # datasets
        address_sys_quads = 'AddressSystemQuadrants'
        counties = 'Counties'
        metro_townships = 'MetroTownships'
        munis = 'Municipalities'
        zips = 'ZipCodes'
        feature_class_list = [address_sys_quads, counties, metro_townships, munis, zips]
        print(feature_class_list)

        # create text file for logging
        log_file = open(projectFolder + "/BoundaryChangesLog_" + formatted_date_with_time + ".txt","w+")
        log_file.write("Log file for CheckForSpatialBoundaryChanges.py \n")
        log_file.write("The following SGID boundaries where checked for changes: " + str(feature_class_list) + "\n")
        log_file.write("Began at: " + str(datetime.datetime.now()) + "\n")


        # create file geodatabase for boundary changes
        changes_fgdb = arcpy.CreateFileGDB_management(projectFolder, changesFGDB)

        DeletePreviousBoundaries()
        RenameExistingDatasets()
        ImportSGIDBoundaries()
        RunSymmetricalDifference()
        GetBoundaryUpdates_Count()

        # compact the boundaries fgdb
        arcpy.Compact_management('D:/BoundaryChanges/Boundaries.gdb')


        print("Done!")
        log_file.write("Finished at: " + str(datetime.datetime.now()) + "\n")
        log_file.close()
        # create the changed fgdb for symmetrical difference output
        #arcpy.CreateFileGDB_management(projectFolder, changesFGDB)
    except Exception as e:
        log_file.write('An exception has occured - %s' % e)


