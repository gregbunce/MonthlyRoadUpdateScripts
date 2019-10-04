import sys
import arcpy
import datetime
import time
from arcpy import env

'''
Notes before running this script:
1. Make sure the 'local_workspace' is location for the intermediate data is correct and the LRS layer is contained in there.  There's a function to import it, if needed.
2. Create a new local_workspace with today's date
3. Import the UDOTRoutes_LRS layer - there is a function call for this the 'Main'.
'''

# get date variables
now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day
hour = now.hour
min = now.minute
formatted_date = str(year) + "_" + str(month) + "_" + str(day)
start_date_time = str(year) + str(month) + str(day) + "_" + str(hour) + str(min)
start_time = time.time()
print str(now)

# text file for logging
text_file_path = "C:\\temp\\AssignMileposts" + start_date_time + ".txt"
file = open(text_file_path, "a")

# global variables
local_workspace = 'C:\\Users\\gbunce\Documents\\projects\\UTRANS\\UpdateMilepostsInRoads_Edit\\2019_08_07.gdb'
arcpy.env.workspace = 'C:\\Users\\gbunce\Documents\\projects\\UTRANS\\UpdateMilepostsInRoads_Edit\\2019_08_07.gdb'
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
    file.write("\n" + "nulled out mp from-values: " + str(nulled_out_from))
    file.write("\n" + "nulled out mp to-values: " + str(nulled_out_to))
    file.write("\n" + "Finished nulling out existing mileposts at: " + str(datetime.datetime.now()))

    edit.stopOperation()
    edit.stopEditing(True)


#: Function to create milepost tables using the 'Feature Vertices To Points" GP tool (getting the 'start' and 'end' of each segment)
def create_new_milepost_values_tables():
    print "Begin Locate Features Along Route at: " + str(datetime.datetime.now())
    file.write("\n" + "\n" + "Begin Locate Features Along Route at: " + str(datetime.datetime.now()))
    # create a feature layer of roads to use only features that have a "LEN(DOT_RTNAME) = 5 and (DOT_RTNAME like '0%')"
    arcpy.MakeFeatureLayer_management(roads_fc, "roads_dot_rtname_lyr", "LEN(DOT_RTNAME) = 5 and (DOT_RTNAME like '0%')")

    # feature vertices to points to get the start/from points and the end/to points for the roads data
    road_from_vertices = arcpy.FeatureVerticesToPoints_management("roads_dot_rtname_lyr", local_workspace + "/Roads_FromVert", point_location="START")
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
    #: Fully qualify the field names.
    #arcpy.env.qualifiedFieldNames = True

    #print "Begin table join at: " + str(datetime.datetime.now())
    #file.write("\n" + "\n" + "Begin table join at: " + str(datetime.datetime.now()))

    # make table view from locate-features-along-routes output tables (only use rows where RID = DOT_RTNAME - this ensures that correct LRS mile for that road segment is used - b/c the milepost tables also have other milepost values for the start/end points of the road segment if other LRS linework intersects that location.  Think of areas where the LRS intersects, so that point may retrun the milepost for both LRS line features.  This query ensures we are getting the correct milepost for that road segment)
    arcpy.MakeTableView_management(table_output, "table_view", "RID = DOT_RTNAME")
    
    # # join the output table to the roads data
    # arcpy.MakeFeatureLayer_management(roads_fc, "roads_lyr")
    # print("Begin joining the milepost table to the UTRANS feature class at ... "+ str(datetime.datetime.now()))
    # joined_tables = arcpy.AddJoin_management(in_layer_or_view="roads_lyr", in_field="UNIQUE_ID", join_table="table_view", join_field="UNIQUE_ID", join_type="KEEP_COMMON")  
    # #print "Finished table join at: " + str(datetime.datetime.now())
    # #file.write("Finished table join at: " + str(datetime.datetime.now()))

    # print "Begin Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now())
    # file.write("\n" + "\n" + "Begin Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now()))
    # # make feature layer of joined tables
    # arcpy.MakeFeatureLayer_management(joined_tables, "joined_feat_lyr")

    edit = arcpy.da.Editor(utrans_conn)
    edit.startEditing(False, True)
    edit.startOperation()

    #: Option A - Using Field Calcuator (I was having issues with this option so for now, I'm using Option B).
    # if str(table_output) == "out_table_from_verts":
    #     arcpy.CalculateField_management("joined_feat_lyr", "UTRANS.TRANSADMIN.Roads_Edit.DOT_F_MILE", "!out_table_from_verts.MEAS!", "PYTHON")

    # if str(table_output) == "out_table_to_verts":
    #     arcpy.CalculateField_management("joined_feat_lyr", "UTRANS.TRANSADMIN.Roads_Edit.DOT_T_MILE", "!out_table_to_verts.MEAS!", "PYTHON")

    # print "Finished Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now())
    # file.write("\n" + "Finished Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now()))


    #: Option B - Using Update Cursor.
    # fields = ["UTRANS.TRANSADMIN.Roads_Edit.DOT_F_MILE", "!out_table_to_verts.MEAS!"]
    # with arcpy.da.UpdateCursor("joined_feat_lyr", fields) as cursor:
    #         for row in cursor:
    #             print(str(row[0]) + " " + str(row[1]))
    #             my_counter = my_counter + 1
    #             row[0] = row[1]
    #             cursor.updateRow(row)
    #             print('Calculated over ' + str(my_counter) + ' values so far.')


    #: Option C - Use dictionary method.
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
                cursor.updateRow(row)
                print "Updated " + str(my_counter) + " " + milepost_field + " records so far.  Still updating..."

    print "Finished updating the Roads_Edit milepost field " + milepost_field +  " with " + str(my_counter) + " new milepost records."

    edit.stopOperation()
    edit.stopEditing(True)

    # remove join and delete temp-layers
    #arcpy.RemoveJoin_management("roads_lyr")
    arcpy.Delete_management("table_view")
    #arcpy.Delete_management("joined_feat_lyr")
    #arcpy.Delete_management("roads_lyr")


#: Use this function if you want to import the SGID roads and LRS into a testing fgdb.
def import_lrs_into_scratch_workspace():
    print "Importing LRS data into scratch workspace"
    file.write("\n" + "\n" + "Began importing sgid lrs into scratch workspace at: " + str(datetime.datetime.now()))
    arcpy.FeatureClassToGeodatabase_conversion(Input_Features="Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.TRANSPORTATION.UDOTRoutes_LRS", Output_Geodatabase=local_workspace)


# Main function.
if __name__ == "__main__":
    try:
        #: Create a text file for logging.
        file.write("Began Assign Mileposts to Roads at: " + str(datetime.datetime.now()))

        #: Import the SGID LRS into scratch fgdb workspace.
        #import_lrs_into_scratch_workspace()
        
        #: 1. Null out existing mileposts.
        print("Begin nulling out existing mileposts at ..." + str(datetime.datetime.now()))
        null_existing_mileposts()

        #: 2. Create the new milepost tables in a temp fgdb.
        print("Begin creating the new milepost tables at ..." + str(datetime.datetime.now()))
        #create_new_milepost_values_tables()

        #: 3. Calculate over the new milepost values from the tables to the feature class.
        print("Begin calculating the new mileposts from the table to the feature class at ..." + str(datetime.datetime.now()))
        field_calculate_milepost_values_to_roads(table_output_from_verts)
        field_calculate_milepost_values_to_roads(table_output_to_verts)

        #: Finished.
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