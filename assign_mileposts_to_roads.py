import sys
import arcpy
import datetime
import time
from arcpy import env

'''
Notes before running this script:
1. Make sure the 'roads_fc' variable is pointing to the desired UTRANS Roads_Edit feature class.
2. Make sure the 'utrans_conn' variable is pointing to the desired UTRANS database connection file.
'''

# get date variables
now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day
hour = now.hour
min = now.minute
formatted_date = str(year) + str(month) + str(day)
start_date_time = str(year) + str(month) + str(day) + "_" + str(hour) + str(min)
start_time = time.time()
print str(now)

# text file for logging
text_file_path = "C:/temp/AssignMileposts" + start_date_time + ".txt"
file = open(text_file_path, "a")

# global variables
local_workspace = 'C:/Users/gbunce/Documents/projects/UTRANS/UpdateMilepostsInRoads_Edit/' + 'UpdateUtransMileposts_' + formatted_date + '.gdb'
arcpy.env.workspace = local_workspace
#roads_fc = 'Database Connections\\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\\UTRANS.TRANSADMIN.Centerlines_Edit\\UTRANS.TRANSADMIN.Roads_Edit' # make fullpath to utrans
roads_fc = 'Database Connections\\TestingConnection@utrans.agrc.utah.gov.sde\\UTRANS.TRANSADMIN.Centerlines_Edit\\UTRANS.TRANSADMIN.Roads_Edit'
lrs_fc ='UDOTRoutes_LRS'
#utrans_conn = 'Database Connections\\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde'
utrans_conn = 'Database Connections\\TestingConnection@utrans.agrc.utah.gov.sde'
table_output_from_verts = "out_table_from_verts"
table_output_to_verts = "out_table_to_verts"


#: Function to null out existing mileposts
def null_existing_mileposts():
    nulled_out_from = 0
    nulled_out_to = 0
    my_counter = 0

    edit = arcpy.da.Editor(utrans_conn)
    edit.startEditing(False, True)
    edit.startOperation()

    #with arcpy.da.Editor(utrans_conn) as edit:
    # start edit session and operation
    #with arcpy.da.Editor(local_workspace) as edit:

    # Begin nulling out the milepost values where "DOT_F_MILE >= 0 or DOT_T_MILE >= 0"
    print "Begin nulling out milepost fields at " + str(datetime.datetime.now())
    file.write("\n" + "\n" + "Began nulling out existing mileposts at: " + str(datetime.datetime.now()))
    fields = ["DOT_F_MILE", "DOT_T_MILE"]
    where_cluase = 'DOT_F_MILE >= 0 or DOT_T_MILE >= 0'
    with arcpy.da.UpdateCursor(roads_fc, fields, where_cluase) as cursor:
            for row in cursor:
                my_counter = my_counter + 1
                if row[0]>=0:
                    row[0] = None
                    nulled_out_from = nulled_out_from + 1
                if row[1]>= 0:
                    row[1] = None
                    nulled_out_to = nulled_out_to + 1
                cursor.updateRow(row)
                print 'Still nulling out records.  On record number ' + str(my_counter) + '. So far we have nulled out ' + str(nulled_out_from) +  ' mileposts.'

    #: Finished nulling out values.
    print "Finished nulling out milepost fields at " + str(datetime.datetime.now())
    print "nulled out mp from-values: " + str(nulled_out_from)
    print "nulled out mp to-values: " + str(nulled_out_to)
    file.write("\n" + "Finished nulling out existing mileposts at: " + str(datetime.datetime.now()))    
    file.write("\n" + "... nulled out mp from-values: " + str(nulled_out_from))
    file.write("\n" + "... nulled out mp to-values: " + str(nulled_out_to))

    edit.stopOperation()
    edit.stopEditing(True)


#: Function to create milepost tables using the 'Feature Vertices To Points" GP tool (getting the 'start' and 'end' of each segment)
def create_new_milepost_values_tables():
    print "Begin Locate Features Along Route at: " + str(datetime.datetime.now())
    file.write("\n" + "\n" + "Begin Locate Features Along Route at: " + str(datetime.datetime.now()))
    # create a feature layer of roads to use only features that have a "LEN(DOT_RTNAME) = 5 and (DOT_RTNAME like '0%')"
    arcpy.MakeFeatureLayer_management(roads_fc, "roads_dot_rtname_lyr", "LEN(DOT_RTNAME) = 5 and (DOT_RTNAME like '0%')")

    # feature vertices to points to get the start/from points and the end/to points for the roads data
    print "Begin creating the feature class: " + local_workspace + "/Roads_FromVert"
    road_from_vertices = arcpy.FeatureVerticesToPoints_management("roads_dot_rtname_lyr", local_workspace + "/Roads_FromVert", point_location="START")
    print "Begin creating the feature class: " + local_workspace + "/Roads_ToVert"
    road_to_vertices = arcpy.FeatureVerticesToPoints_management("roads_dot_rtname_lyr", local_workspace + "/Roads_ToVert", point_location="END")
    arcpy.MakeFeatureLayer_management(road_from_vertices, "roads_from_verts_lyr")
    arcpy.MakeFeatureLayer_management(road_to_vertices, "roads_to_verts_lyr")

    # locate features along route
    ## this is for road line features but it only honors the direction of the LRS and not the road arc direction.  table_output = arcpy.LocateFeaturesAlongRoutes_lr("roads_dot_rtname_lyr", lrs_fc, route_id_field="LABEL", radius_or_tolerance="0 Meters", out_table="D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/locate_feat_output", out_event_properties="RID LINE FMEAS TMEAS", route_locations="FIRST", distance_field="DISTANCE", zero_length_events="ZERO", in_fields="FIELDS", m_direction_offsetting="NO_M_DIRECTION")
    # table_output = r"D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/locate_feat_output"
    table_output_from_verts = arcpy.LocateFeaturesAlongRoutes_lr("roads_from_verts_lyr", in_routes="UDOTRoutes_LRS", route_id_field="LABEL", radius_or_tolerance="0 Meters", out_table="out_table_from_verts", out_event_properties="RID POINT MEAS", route_locations="ALL", distance_field="DISTANCE", zero_length_events="ZERO", in_fields="FIELDS", m_direction_offsetting="M_DIRECTON")
    table_output_to_verts = arcpy.LocateFeaturesAlongRoutes_lr("roads_to_verts_lyr", in_routes="UDOTRoutes_LRS", route_id_field="LABEL", radius_or_tolerance="0 Meters", out_table="out_table_to_verts", out_event_properties="RID POINT MEAS", route_locations="ALL", distance_field="DISTANCE", zero_length_events="ZERO", in_fields="FIELDS", m_direction_offsetting="M_DIRECTON")

    print "Finished Locating Features Along Route at: " + str(datetime.datetime.now())
    file.write("\n" + "Finished Locating Features Along Route at: " + str(datetime.datetime.now()))



#: Function to calculate over the milepost values from the fgdb temp tables to the UTRANS Roads feature class.
def field_calculate_milepost_values_to_roads(table_output):
    # make table view from locate-features-along-routes output tables (only use rows where RID = DOT_RTNAME - this ensures that correct LRS mile for that road segment is used - b/c the milepost tables also have other milepost values for the start/end points of the road segment if other LRS linework intersects that location.  Think of areas where the LRS intersects, so that point may retrun the milepost for both LRS line features.  This query ensures we are getting the correct milepost for that road segment)
    arcpy.MakeTableView_management(table_output, "table_view", "RID = DOT_RTNAME")

    edit = arcpy.da.Editor(utrans_conn)
    edit.startEditing(False, True)
    edit.startOperation()

    # Create a dictionary of values from the milepost table and then use that in an UpdateCursor to update Roads_Edit.
    my_dict = {}
    my_counter = 0
    milepost_field = ''

    #: Populate the python dictionary with values from the apporpriate milepost gp-tool output table.
    with arcpy.da.SearchCursor('table_view', ['UNIQUE_ID', 'MEAS']) as cur:
        for row in cur:
            my_dict[row[0]] = row[1]

    #: Use update cursor and python dictionary to update the Roads_Edit milepost fields
    if str(table_output) == "out_table_from_verts":
        milepost_field = 'DOT_F_MILE'
    if str(table_output) == "out_table_to_verts":
        milepost_field = 'DOT_T_MILE'
    fields = ["UNIQUE_ID", milepost_field]

    with arcpy.da.UpdateCursor(roads_fc, fields, "LEN(DOT_RTNAME) = 5 and (DOT_RTNAME like '0%')") as cursor: # limit the cursor to only use records that might contain milepost values (same query was used above to create the milpost tables). 
            for row in cursor:
                my_counter = my_counter + 1
                #: If the Road_Edits' UNIQUE_ID is in the dictionary, then assign it's value to the appropriate milepost field.
                if row[0] in my_dict:
                    row[1] = my_dict[row[0]]
                    print "Updated " + str(my_counter) + " " + milepost_field + " records so far.  Still updating..."
                cursor.updateRow(row)

    print "Finished updating the Roads_Edit milepost field " + milepost_field +  " with " + str(my_counter) + " new milepost records."

    edit.stopOperation()
    edit.stopEditing(True)
    arcpy.Delete_management("table_view")

    file.write("\n" + "Finished assigning new mileposts to " + milepost_field +  " at: " + str(datetime.datetime.now()))
    file.write("\n" + "... assigned " + str(my_counter)) + " new values to " + milepost_field



#: Function to create the scratch workspace and then import the needed SGID LRS layer.
def create_scratch_workspace_import_lrs():
    print "Creating scratch fgdb workspace..."
    arcpy.CreateFileGDB_management("C:/Users/gbunce/Documents/projects/UTRANS/UpdateMilepostsInRoads_Edit/", "UpdateUtransMileposts_" + formatted_date + ".gdb")

    print "Importing LRS data into scratch workspace "
    file.write("\n" + "\n" + "Began importing sgid lrs into scratch workspace at: " + str(datetime.datetime.now()))
    arcpy.FeatureClassToGeodatabase_conversion(Input_Features="Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.TRANSPORTATION.UDOTRoutes_LRS", Output_Geodatabase=local_workspace)


# Main function.
if __name__ == "__main__":
    try:
        #: Create a text file for logging.
        file.write("Began Assign Mileposts to Roads_Edit at: " + str(datetime.datetime.now()))

        #: 1. Create scratch fgdb workspace and import the SGID LRS.
        create_scratch_workspace_import_lrs()
        
        #: 2. Null out existing mileposts.
        print("Begin nulling out existing mileposts at ..." + str(datetime.datetime.now()))
        null_existing_mileposts()

        #: 3. Create the new milepost tables in a temp fgdb.
        print("Begin creating the new milepost tables at ..." + str(datetime.datetime.now()))
        create_new_milepost_values_tables()

        #: 4. Calculate over the new milepost values from the tables to the feature class.
        print("Begin calculating the new mileposts from the table to the feature class at ..." + str(datetime.datetime.now()))
        field_calculate_milepost_values_to_roads(table_output_from_verts)
        field_calculate_milepost_values_to_roads(table_output_to_verts)

        #: 5. Finished.
        file.write("\n" + "Finished Assign Mileposts to Roads at: " + str(datetime.datetime.now()))
        print "Finished Assign Mileposts to Roads at: " + str(datetime.datetime.now())
        elapsed_time = (time.time() - start_time) / 60 # divide by 60 to get mins (it's in secs)
        print "Total run time: " + str(elapsed_time) + " mins"
        file.write("\n" + "\n" + "Total run time: " + str(elapsed_time))
        file.close()
        print "done!"
    except Exception:
        e = sys.exc_info()[1]
        print str(e.args[0])
        print str(arcpy.GetMessages(2))
        file.write("\n" + "ERROR MESSAGE from sys.exe_info: " + e.args[0]+ "\n")
        file.write("\n" + "ERROR MESSAGE from arcpy.GetMessages(2): " + arcpy.GetMessages(2))
        file.close()
        #log_file.write('An exception has occured - %s' % e)