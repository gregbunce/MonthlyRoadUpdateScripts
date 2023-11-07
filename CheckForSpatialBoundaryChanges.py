# Use Python2 or update data connection files to pro connections.

import arcpy, os, datetime

# this runs as on a weekly scheduled task on my machine (for now - then maybe forklift after testing)
# Note: search for "##" and switch out lines when going live to sde roads editing

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
    try:
        # switch workspace for this function (.ListDatasets)
        arcpy.env.workspace = str(changes_fgdb)
        ##arcpy.env.workspace = 'D:\\BoundaryChanges\\Changes_2018_7_2.gdb'

        # loop through the feature classes and get count if feature class name conatins SymDiff_
        for fc in arcpy.ListFeatureClasses():
            count = arcpy.GetCount_management(fc)
            log_file.write(str(fc) + " Change Count: " + str(count) + "\n")
            print(str(fc) + " Change Count: " + str(count))

            # Null out spatial values for these fields
            if int(count[0]) > 0:
                NullOutSpatialValuesIfChangesFound(fc)
    except Exception:
        e = sys.exc_info()[1]
        print("GetBoundaryUpdates_Count Error: " + e.args[0])
        log_file.write("GetBoundaryUpdates_Count ERROR MESSAGE: " + e.args[0] + "\n")

def NullOutSpatialValuesIfChangesFound(sgid_polygon_containing_edits):
    try:
        field_array = []
        if str(sgid_polygon_containing_edits) == "SymDiff_AddressSystemQuadrants":
            field_array = ['QUADRANT_L', 'QUADRANT_R', 'ADDRSYS_L', 'ADDRSYS_R']
        elif str(sgid_polygon_containing_edits) == "SymDiff_Counties":
            field_array = ['COUNTY_L', 'COUNTY_R']
        elif str(sgid_polygon_containing_edits) == "SymDiff_MetroTownships":
            field_array = ['UNINCCOM_L', 'UNINCCOM_R']
        elif str(sgid_polygon_containing_edits) == "SymDiff_Municipalities":
            field_array = ['INCMUNI_L', 'INCMUNI_R']
        elif str(sgid_polygon_containing_edits) == "SymDiff_ZipCodes":
            field_array = ['POSTCOMM_L', 'POSTCOMM_R', 'ZIPCODE_L', 'ZIPCODE_R']
        else:
            log_file.write("Did not null values in UTRANS Roads_Edit for related spatial polygon because it did not recognize the parameter: " + str(sgid_polygon_containing_edits) + "\n")
    
        ##database_connection = 'Database Connections\\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde' # edit on sde EDIT version data
        database_connection = 'Database Connections\gbunce@utrans.agrc.utah.gov.sde' # edit on sde my-user's version data
        ##roads_feature_class = 'UTRANS.TRANSADMIN.Centerlines_Edit\\UTRANS.TRANSADMIN.Roads_Edit' # (use for UTRANS)
        ##database_connection = 'D:\\BoundaryChanges\\NullValueTesting.gdb' # (use for FileGeoDatabase)
        ##roads_feature_class = '\\Roads_Edit' # (use for FileGeoDatabase)
        roads_feature_class = '\\UTRANS.TRANSADMIN.Centerlines_Edit\\UTRANS.TRANSADMIN.Roads_Edit' # (use for UTRANS)

        # Open an edit session and start an edit operation
        edit = arcpy.da.Editor(database_connection)
        # Edit session is started without an undo/redo stack for versioned data
        #(for second argument, use False for unversioned data)
        # edit.startEditing ({with_undo}, {multiuser_mode})
        edit.startEditing(False, True) # for versioned data (use for UTRANS)
        ##edit.startEditing(False, False) # for unversioned data - (use for FileGeoDatabase)
        edit.startOperation()

        # Make a layer and select cities which overlap the chihuahua polygon
        arcpy.MakeFeatureLayer_management(database_connection + roads_feature_class, 'roads_lyr') 
        arcpy.MakeFeatureLayer_management(sgid_polygon_containing_edits, 'boundary_changes_lyr')
        arcpy.SelectLayerByLocation_management('roads_lyr', 'INTERSECT', 'boundary_changes_lyr')

        cursor = arcpy.da.UpdateCursor('roads_lyr', field_array) #, query)

        # Loop through rows & create temporary dictionary of values
        for row in cursor:
            # null values for the appropriate fields
            row_index = 0
            for field in field_array:
                print(str(field))
                #row.setValue(field, None)
                row[row_index] = None
                row_index = row_index + 1
            cursor.updateRow(row)
        del cursor
        del row
        edit.stopOperation()
        edit.stopEditing(True)
        log_file.write("  Nulled-out attributes for the following fields: " + str(field_array) + "\n")
    except Exception:
        e = sys.exc_info()[1]
        print("NullOutSpatialValuesIfChangesFound Error: " + e.args[0])
        log_file.write("NullOutSpatialValuesIfChangesFound ERROR MESSAGE: " + e.args[0] + "\n")

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
        arcpy.env.workspace = 'C:/Users/gbunce/Documents/BoundaryChanges/Boundaries.gdb'
        boundaryFGDB = 'Boundaries.gdb'
        changesFGDB = 'Changes_' + formatted_date + '.gdb'
        projectFolder = 'C:/Users/gbunce/Documents/BoundaryChanges'
        sgid_connection = 'Database Connections/internal@SGID@internal.agrc.utah.gov.sde/SGID.'

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
        arcpy.Compact_management('C:/Users/gbunce/Documents/BoundaryChanges/Boundaries.gdb')

        print("Done!")
        log_file.write("Finished at: " + str(datetime.datetime.now()) + "\n")
        log_file.close()
    except Exception:
        e = sys.exc_info()[1]
        print(e.args[0])
        log_file.write("ERROR MESSAGE: " + e.args[0]+ "\n")
        #log_file.write('An exception has occured - %s' % e)
