import arcpy
import datetime
import time
from arcpy import env

## notes before running this script: Make sure the 'local_workspace' is location for the intermediate data and the LRS.
## Create a new local_workspace with today's date
## Import the UDOTRoutes_LRS layer

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
roads_fc = 'Database Connections\\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\\UTRANS.TRANSADMIN.Centerlines_Edit\\UTRANS.TRANSADMIN.Roads_Edit' # make fullpath to utrans
lrs_fc ='UDOTRoutes_LRS'
utrans_conn = 'Database Connections\\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde'
table_output_from_verts = "out_table_from_verts"
table_output_to_verts = "out_table_to_verts"

def null_existing_mileposts():
    nulled_out_from = 0
    nulled_out_to = 0

    edit = arcpy.da.Editor(utrans_conn)
    edit.startEditing(False, True)
    edit.startOperation()

    #with arcpy.da.Editor(utrans_conn) as edit:
    # start edit session and operation
    #with arcpy.da.Editor(local_workspace) as edit:
    
    # null out the milepost values where "DOT_F_MILE >= 0 or DOT_T_MILE >= 0"
    print "Begin nulling out milepost fields at " + str(datetime.datetime.now())
    file.write("\n" + "\n" + "Began nulling out existing mileposts at: " + str(datetime.datetime.now()))
    fields    = ("DOT_F_MILE", "DOT_T_MILE")
    with arcpy.da.UpdateCursor(roads_fc, fields) as cursor:
            for row in cursor:
                if row[0]>=0:
                    row[0] = None
                    nulled_out_from = nulled_out_from + 1
                if row[1]>= 0:
                    row[1] = None
                    nulled_out_to = nulled_out_to + 1
                cursor.updateRow(row)
    print "Finished nulling out milepost fields at " + str(datetime.datetime.now())
    print "nulled out mp from-values: " + str(nulled_out_from)
    print "nulled out mp to-values: " + str(nulled_out_to)
    file.write("\n" + "nulled out mp from-values: " + str(nulled_out_from))
    file.write("\n" + "nulled out mp to-values: " + str(nulled_out_to))
    file.write("\n" + "Finished nulling out existing mileposts at: " + str(datetime.datetime.now()))

    del cursor
    del row
    edit.stopOperation()
    edit.stopEditing(True)



def create_new_milepost_values_tables():
    print "Begin Locate Features Along Route at: " + str(datetime.datetime.now())
    file.write("\n" + "\n" + "Begin Locate Features Along Route at: " + str(datetime.datetime.now()))
    # create a feature layer of roads to use only features that have a "LEN(DOT_RTNAME) = 5 and (DOT_RTNAME like '0%')"
    arcpy.MakeFeatureLayer_management(roads_fc, "roads_dot_rtname_lyr", "CHAR_LENGTH(DOT_RTNAME) = 5 and (DOT_RTNAME like '0%')")

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



def field_calculate_milepost_values_to_roads(table_output):
    #print "Begin table join at: " + str(datetime.datetime.now())
    #file.write("\n" + "\n" + "Begin table join at: " + str(datetime.datetime.now()))

    # make table view from locate-features-along-routes output tables
    arcpy.MakeTableView_management(table_output, "table_view", "RID = DOT_RTNAME")
    
    # join the output table to the roads data
    arcpy.MakeFeatureLayer_management(roads_fc, "roads_lyr")
    joined_tables = arcpy.AddJoin_management(in_layer_or_view="roads_lyr", in_field="UNIQUE_ID", join_table="table_view", join_field="UNIQUE_ID", join_type="KEEP_COMMON")  
    #print "Finished table join at: " + str(datetime.datetime.now())
    #file.write("Finished table join at: " + str(datetime.datetime.now()))

    print "Begin Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now())
    file.write("\n" + "\n" + "Begin Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now()))
    # make feature layer of joined tables
    arcpy.MakeFeatureLayer_management(joined_tables, "joined_feat_lyr")
    
    edit = arcpy.da.Editor(utrans_conn)
    edit.startEditing(False, True)
    edit.startOperation()

    #with arcpy.da.Editor(utrans_conn) as edit:
    if str(table_output) == "out_table_from_verts":
        arcpy.CalculateField_management("joined_feat_lyr", "Roads.DOT_F_MILE", "!out_table_from_verts.MEAS!", "PYTHON")
    
    if str(table_output) == "out_table_to_verts":
        arcpy.CalculateField_management("joined_feat_lyr", "Roads.DOT_T_MILE", "!out_table_to_verts.MEAS!", "PYTHON")

    print "Finished Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now())
    file.write("\n" + "Finished Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now()))
    
    edit.stopOperation()
    edit.stopEditing(True)

    # remove join and delete temp-layers
    arcpy.RemoveJoin_management("roads_lyr")
    arcpy.Delete_management("table_view")
    arcpy.Delete_management("joined_feat_lyr")
    arcpy.Delete_management("roads_lyr")


def import_sgid_roads_and_lrs_into_fgdb():
    print "import sgid roads and lrs data into fgdb"
    file.write("\n" + "\n" + "Began importing roads and lrs into testing lrs fgdb at: " + str(datetime.datetime.now()))
    arcpy.FeatureClassToGeodatabase_conversion(Input_Features="'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.TRANSPORTATION.UDOTRoutes_LRS';'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.TRANSPORTATION.Roads'", Output_Geodatabase=workspace)


# Main function
if __name__ == "__main__":
    try:
        # create text file for logging
        file.write("Began Assign Mileposts to Roads at: " + str(datetime.datetime.now()))

        # import_sgid_roads_and_lrs_into_fgdb() # just for testing

        # start and edit session and call functions that perform edits
        #with arcpy.da.Editor(local_workspace) as edit:
        null_existing_mileposts()
        create_new_milepost_values_tables()
        field_calculate_milepost_values_to_roads(table_output_from_verts)
        field_calculate_milepost_values_to_roads(table_output_to_verts)

        # finished
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