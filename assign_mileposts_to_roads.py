import arcpy
import datetime

## notes before running this script: Make sure the 'workspace' is location for the roads you want:  Update the "Roads" layer in the workspace and remove the output tables

# get date variables
now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day
hour = now.hour
min = now.minute
formatted_date = str(year) + "_" + str(month) + "_" + str(day)
formatted_date_with_time = str(year) + str(month) + str(day) + "_" + str(hour) + str(min)
print str(now)

# text file for logging
text_file_path = r"C:\temp\AssignMileposts" + formatted_date_with_time + ".txt"
file = open(text_file_path, "a")

# global variables
workspace = r'D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb'
roads_fc = r'D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\Roads'
lrs_fc = r'D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\UDOTRoutes_LRS'
table_output_from_verts = "D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/out_table_from_verts"
table_output_to_verts = "D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/out_table_to_verts"

def null_existing_mileposts():
    nulled_out_from = 0
    nulled_out_to = 0
    
    # start edit session and operation
    #with arcpy.da.Editor(workspace) as edit:
    # null out the milepost values where "DOT_F_MILE >= 0 or DOT_T_MILE >= 0"
    print "Begin nulling out milepost fields at " + str(datetime.datetime.now())
    file.write("\n" + "Began nulling out existing mileposts at: " + str(datetime.datetime.now()))
    fields    = ("DOT_F_MILE", "DOT_T_MILE")
    with arcpy.da.UpdateCursor(roads_fc, fields) as Cursor:
            for row in Cursor:
                if row[0]>=0:
                    row[0] = None
                    nulled_out_from = nulled_out_from + 1
                if row[1]>= 0:
                    row[1] = None
                    nulled_out_to = nulled_out_to + 1
                Cursor.updateRow(row)
    print "Finished nulling out milepost fields at " + str(datetime.datetime.now())
    print "nulled out mp from-values: " + str(nulled_out_from)
    print "nulled out mp to-values: " + str(nulled_out_to)
    file.write("\n" + "nulled out mp from-values: " + str(nulled_out_from))
    file.write("\n" + "nulled out mp to-values: " + str(nulled_out_to))
    file.write("\n" + "Finished nulling out existing mileposts at: " + str(datetime.datetime.now()))


def create_new_milepost_values_tables():
    print "Begin Locate Features Along Route at: " + str(datetime.datetime.now())
    file.write("\n" + "Begin Locate Features Along Route at: " + str(datetime.datetime.now()))

    # create a feature layer of roads to use only features that have a "LEN(DOT_RTNAME) = 5 and (DOT_RTNAME like '0%')"
    arcpy.MakeFeatureLayer_management(roads_fc, "roads_dot_rtname_lyr", "CHAR_LENGTH(DOT_RTNAME) = 5 and (DOT_RTNAME like '0%')")

    # feature vertices to points to get the start/from points and the end/to points for the roads data
    road_from_vertices = arcpy.FeatureVerticesToPoints_management("roads_dot_rtname_lyr", workspace + "/Roads_FromVert", point_location="START")
    road_to_vertices = arcpy.FeatureVerticesToPoints_management("roads_dot_rtname_lyr", workspace + "/Roads_ToVert", point_location="END")
    arcpy.MakeFeatureLayer_management(road_from_vertices, "roads_from_verts_lyr")
    arcpy.MakeFeatureLayer_management(road_to_vertices, "roads_to_verts_lyr")

    # locate features along route
    ## this is for road line features but it only honors the direction of the LRS and not the road arc direction.  table_output = arcpy.LocateFeaturesAlongRoutes_lr("roads_dot_rtname_lyr", lrs_fc, route_id_field="LABEL", radius_or_tolerance="0 Meters", out_table="D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/locate_feat_output", out_event_properties="RID LINE FMEAS TMEAS", route_locations="FIRST", distance_field="DISTANCE", zero_length_events="ZERO", in_fields="FIELDS", m_direction_offsetting="NO_M_DIRECTION")
    # table_output = r"D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/locate_feat_output"
    table_output_from_verts = arcpy.LocateFeaturesAlongRoutes_lr("roads_from_verts_lyr", in_routes="D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/UDOTRoutes_LRS", route_id_field="LABEL", radius_or_tolerance="0 Meters", out_table="D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/out_table_from_verts", out_event_properties="RID POINT MEAS", route_locations="ALL", distance_field="DISTANCE", zero_length_events="ZERO", in_fields="FIELDS", m_direction_offsetting="M_DIRECTON")
    table_output_to_verts = arcpy.LocateFeaturesAlongRoutes_lr("roads_to_verts_lyr", in_routes="D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/UDOTRoutes_LRS", route_id_field="LABEL", radius_or_tolerance="0 Meters", out_table="D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/out_table_to_verts", out_event_properties="RID POINT MEAS", route_locations="ALL", distance_field="DISTANCE", zero_length_events="ZERO", in_fields="FIELDS", m_direction_offsetting="M_DIRECTON")    

    # remove rows where the start or end vertex found the wrong lrs feature
    #arcpy.TableToTable_conversion(in_rows="D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/out_table_from_verts_all", out_path="D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb", out_name="out_table_from_verts", where_clause="RID = DOT_RTNAME", field_mapping="""RID "RID" true true false 15 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts_all,RID,-1,-1;MEAS "MEAS" true true false 8 Double 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts_all,MEAS,-1,-1;Distance "Distance" true true false 8 Double 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,Distance,-1,-1;STATUS "ConstructedStatus" true true false 15 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,STATUS,-1,-1;CARTOCODE "CartographicCode" true true false 10 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,CARTOCODE,-1,-1;FULLNAME "FullName" true true false 50 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,FULLNAME,-1,-1;FROMADDR_L "LeftFromAddress" true true false 4 Long 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,FROMADDR_L,-1,-1;TOADDR_L "LeftToAddress" true true false 4 Long 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,TOADDR_L,-1,-1;FROMADDR_R "RightFromAddress" true true false 4 Long 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,FROMADDR_R,-1,-1;TOADDR_R "RightToAddress" true true false 4 Long 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,TOADDR_R,-1,-1;PARITY_L "ParityLeft" true true false 1 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,PARITY_L,-1,-1;PARITY_R "ParityRight" true true false 1 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,PARITY_R,-1,-1;PREDIR "StreetNamePreDirectional" true true false 2 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,PREDIR,-1,-1;NAME "StreetName" true true false 40 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,NAME,-1,-1;POSTTYPE "StreetNamePostType" true true false 4 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,POSTTYPE,-1,-1;POSTDIR "StreetNamePostDirectional" true true false 2 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,POSTDIR,-1,-1;AN_NAME "AliasNumericStreetName" true true false 10 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,AN_NAME,-1,-1;AN_POSTDIR "AliasNumericPostDirectional" true true false 2 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,AN_POSTDIR,-1,-1;A1_PREDIR "Alias1PreDirectional" true true false 2 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,A1_PREDIR,-1,-1;A1_NAME "Alias1StreetName" true true false 40 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,A1_NAME,-1,-1;A1_POSTTYPE "Alias1PostType" true true false 4 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,A1_POSTTYPE,-1,-1;A1_POSTDIR "Alias1PostDirectional" true true false 2 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,A1_POSTDIR,-1,-1;A2_PREDIR "Alias2PreDirectional" true true false 2 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,A2_PREDIR,-1,-1;A2_NAME "Alias2StreetName" true true false 40 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,A2_NAME,-1,-1;A2_POSTTYPE "Alias2PostType" true true false 4 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,A2_POSTTYPE,-1,-1;A2_POSTDIR "Alias2PostDirectional" true true false 2 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,A2_POSTDIR,-1,-1;QUADRANT_L "QuadrantLeftAddressSystem" true true false 2 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,QUADRANT_L,-1,-1;QUADRANT_R "QuadrantRightAddressSystem" true true false 2 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,QUADRANT_R,-1,-1;STATE_L "StateLeft" true true false 2 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,STATE_L,-1,-1;STATE_R "StateRight" true true false 2 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,STATE_R,-1,-1;COUNTY_L "CountyLeft" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,COUNTY_L,-1,-1;COUNTY_R "CountyRight" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,COUNTY_R,-1,-1;ADDRSYS_L "AddressSystemLeft" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,ADDRSYS_L,-1,-1;ADDRSYS_R "AddressSystemRight" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,ADDRSYS_R,-1,-1;POSTCOMM_L "PostalCommunityNameLeft" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,POSTCOMM_L,-1,-1;POSTCOMM_R "PostalCommunityNameRight" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,POSTCOMM_R,-1,-1;ZIPCODE_L "PostalZipCodeLeft" true true false 5 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,ZIPCODE_L,-1,-1;ZIPCODE_R "PostalZipCodeRight" true true false 5 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,ZIPCODE_R,-1,-1;INCMUNI_L "IncorporatedMunicipalityLeft" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,INCMUNI_L,-1,-1;INCMUNI_R "IncorporatedMunicipalityRight" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,INCMUNI_R,-1,-1;UNINCCOM_L "UnincorporatedMunicipalityLeft" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,UNINCCOM_L,-1,-1;UNINCCOM_R "UnincorporatedMunicipalityRight" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,UNINCCOM_R,-1,-1;NBRHDCOM_L "NeighborhoodCommunityLeft" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,NBRHDCOM_L,-1,-1;NBRHDCOM_R "NeighborhoodCommunityRight" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,NBRHDCOM_R,-1,-1;ER_CAD_ZONES "TBD" true true false 255 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,ER_CAD_ZONES,-1,-1;ESN_L "ESNLeft" true true false 5 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,ESN_L,-1,-1;ESN_R "ESNRight" true true false 5 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,ESN_R,-1,-1;MSAGCOMM_L "MSAGCommunityLeft" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,MSAGCOMM_L,-1,-1;MSAGCOMM_R "MSAGCommunityRight" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,MSAGCOMM_R,-1,-1;ONEWAY "OneWayCode" true true false 1 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,ONEWAY,-1,-1;VERT_LEVEL "VerticalLevel" true true false 1 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,VERT_LEVEL,-1,-1;SPEED_LMT "PostedSpeedLimit" true true false 2 Short 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,SPEED_LMT,-1,-1;ACCESSCODE "AccessIssueCode" true true false 1 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,ACCESSCODE,-1,-1;DOT_HWYNAM "DOTHighwayName" true true false 15 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_HWYNAM,-1,-1;DOT_RTNAME "DOTRouteName" true true false 11 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_RTNAME,-1,-1;DOT_RTPART "DOTRoutePart" true true false 3 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_RTPART,-1,-1;DOT_F_MILE "DOTFromMilepost" true true false 8 Double 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_F_MILE,-1,-1;DOT_T_MILE "DOTToMilepost" true true false 8 Double 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_T_MILE,-1,-1;DOT_FCLASS "DOTFunctional Class" true true false 20 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_FCLASS,-1,-1;DOT_SRFTYP "DOTSurfaceType" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_SRFTYP,-1,-1;DOT_CLASS "DOTRoadFundingClass" true true false 1 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_CLASS,-1,-1;DOT_OWN_L "DOTRoadOwnLeft" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_OWN_L,-1,-1;DOT_OWN_R "DOTRoadOwnRight" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_OWN_R,-1,-1;DOT_AADT "DOTDailyTrafficVolume" true true false 4 Long 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_AADT,-1,-1;DOT_AADTYR "DOTAADTYear" true true false 4 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_AADTYR,-1,-1;DOT_THRULANES "DOTThruLanes" true true false 2 Short 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,DOT_THRULANES,-1,-1;BIKE_L "BikeFeatureLeft" true true false 4 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,BIKE_L,-1,-1;BIKE_R "BikeFeatureRight" true true false 4 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,BIKE_R,-1,-1;BIKE_PLN_L "BikeFeatureStatusLeft" true true false 15 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,BIKE_PLN_L,-1,-1;BIKE_PLN_R "BikeFeatureStatusRight" true true false 15 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,BIKE_PLN_R,-1,-1;BIKE_REGPR "BikeRegionalPriority" true true false 5 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,BIKE_REGPR,-1,-1;BIKE_NOTES "BikeNotes" true true false 50 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,BIKE_NOTES,-1,-1;UNIQUE_ID "UniqueID" true true false 75 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,UNIQUE_ID,-1,-1;LOCAL_UID "LocalUniqueID" true true false 30 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,LOCAL_UID,-1,-1;UTAHRD_UID "UtahRoadUniqueID" true true false 100 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,UTAHRD_UID,-1,-1;SOURCE "SourceOfData" true true false 75 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,SOURCE,-1,-1;UPDATED "DateUpdated" true true false 8 Date 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,UPDATED,-1,-1;EFFECTIVE "EffectiveDate" true true false 8 Date 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,EFFECTIVE,-1,-1;EXPIRE "ExpirationDate" true true false 8 Date 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,EXPIRE,-1,-1;CREATED "CreatedDate" true true false 8 Date 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,CREATED,-1,-1;CUSTOMTAGS "CustomTagBasedAttributes" true true false 1000 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,CUSTOMTAGS,-1,-1;PED_L "Pedestrian Left" true true false 25 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,PED_L,-1,-1;PED_R "Pedestrian Right" true true false 25 Text 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,PED_R,-1,-1;ORIG_FID "ORIG_FID" true true false 4 Long 0 0 ,First,#,D:\UTRANS\UpdateMilepostsInRoads_Edit\testing.gdb\out_table_from_verts,ORIG_FID,-1,-1""", config_keyword="")
    

    print "Finished Locating Features Along Route at: " + str(datetime.datetime.now())
    file.write("\n" + "Finished Locating Features Along Route at: " + str(datetime.datetime.now()))


def field_calculate_milepost_values_to_roads(table_output):
    print str(table_output)
    # make table view from locate-features-along-routes output tables
    arcpy.MakeTableView_management(table_output, "table_view", "RID = DOT_RTNAME")
    
    # join the output table to the roads data
    print "Begin table join at: " + str(datetime.datetime.now())
    file.write("\n" + "Begin table join at: " + str(datetime.datetime.now()))
    arcpy.MakeFeatureLayer_management(roads_fc, "roads_lyr")
    joined_tables = arcpy.AddJoin_management(in_layer_or_view="roads_lyr", in_field="UNIQUE_ID", join_table="table_view", join_field="UNIQUE_ID", join_type="KEEP_COMMON")  
    print "Finished table join at: " + str(datetime.datetime.now())
    file.write("\n" + "Finished table join at: " + str(datetime.datetime.now()))

    print "Begin Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now())
    file.write("\n" + "Begin Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now()))
    # make feature layer of joined tables
    arcpy.MakeFeatureLayer_management(joined_tables, "joined_feat_lyr")
    
    if str(table_output) == "D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/out_table_from_verts":
        arcpy.CalculateField_management("joined_feat_lyr", "Roads.DOT_F_MILE", "!out_table_from_verts.MEAS!", "PYTHON")
    
    if str(table_output) == "D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb/out_table_to_verts":
        arcpy.CalculateField_management("joined_feat_lyr", "Roads.DOT_T_MILE", "!out_table_to_verts.MEAS!", "PYTHON")

    print "Finished Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now())
    file.write("\n" + "Finished Calculating over values from " + str(table_output) + " at: " + str(datetime.datetime.now()))
    
    
    # remove join
    arcpy.RemoveJoin_management("roads_lyr")
    arcpy.Delete_management("table_view")
    arcpy.Delete_management("joined_feat_lyr")
    arcpy.Delete_management("roads_lyr")

def import_sgid_roads_and_lrs_into_fgdb():
    file.write("Began importing roads and lrs into testing lrs fgdb at: " + str(datetime.datetime.now()))
    arcpy.FeatureClassToGeodatabase_conversion(Input_Features="'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.TRANSPORTATION.UDOTRoutes_LRS';'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.TRANSPORTATION.Roads'", Output_Geodatabase="D:/UTRANS/UpdateMilepostsInRoads_Edit/testing.gdb")


# Main function
if __name__ == "__main__":
    try:
        # create text file for logging
        file.write("Began Assign Mileposts to Roads at: " + str(datetime.datetime.now()))

        #import_sgid_roads_and_lrs_into_fgdb() # just for testing
        # start and edit session and call functions that perform edits
        with arcpy.da.Editor(workspace) as edit:
            null_existing_mileposts()
            #create_new_milepost_values_tables()
            field_calculate_milepost_values_to_roads(table_output_from_verts)
            field_calculate_milepost_values_to_roads(table_output_to_verts)

        # finished
        file.write("\n" + "Finished Assign Mileposts to Roads at: " + str(datetime.datetime.now()))
        file.close()
        print "Finished Assign Mileposts to Roads at: " + str(datetime.datetime.now())
        print "done!"
    except Exception:
        e = sys.exc_info()[1]
        print str(e.args[0])
        print str(arcpy.GetMessages(2))
        file.write("\n" + "ERROR MESSAGE from sys.exe_info: " + e.args[0]+ "\n")
        file.write("\n" + "ERROR MESSAGE from arcpy.GetMessages(2): " + arcpy.GetMessages(2))
        file.close()
        #log_file.write('An exception has occured - %s' % e)
