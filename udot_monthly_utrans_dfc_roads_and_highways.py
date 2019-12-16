#: use python 3
#: update the following variables based on the current run [current_update_fc, snapshot_base_fc]

# Import system modules
import os
import arcpy
from arcpy import env
import time

#: set the input datasets
current_update_fc = 'C:\\Users\\gbunce\\Documents\\projects\\UTRANS\\udot_monthly_change_detection\\script_testing\\udot_change_detection_testing.gdb\\update_roads_washCo'  #: current utrans exprot to fgdb.
snapshot_base_fc = 'C:\\Users\\gbunce\\Documents\\projects\\UTRANS\\udot_monthly_change_detection\\script_testing\\udot_change_detection_testing.gdb\\base_roads_washCo'   #: snapshot of utrans from last run.
#utrans_road_changes = 'C:\\Users\\gbunce\\Documents\\projects\\UTRANS\\udot_monthly_change_detection\\script_testing\\udot_dfc_testing2.gdb\\utrans_road_changes'

#: get the directory path
dirname = os.path.dirname(arcpy.Describe(current_update_fc).catalogPath)
desc = arcpy.Describe(dirname)
if hasattr(desc, "datasetType") and desc.datasetType=='FeatureDataset':
    dirname = os.path.dirname(dirname)

#: set the dfc tool outputs
dfc_output_fc = dirname + "\\dfc_output_fc"
dfc_output_matchtable = dirname + "\\dfc_output_matchtable"

print("begin dfc at: " + time.strftime("%c"))

arcpy.management.DetectFeatureChanges(
    update_features=current_update_fc, 
    base_features=snapshot_base_fc,
    out_feature_class=dfc_output_fc,
    search_distance="50 Meters",
    match_fields="FULLNAME FULLNAME",
    out_match_table=dfc_output_matchtable,
    change_tolerance="50 Meters",
    compare_fields="UNIQUE_ID UNIQUE_ID;COUNTY_L COUNTY_L;COUNTY_R COUNTY_R;DOT_RTNAME DOT_RTNAME;DOT_SRFTYP DOT_SRFTYP;DOT_CLASS DOT_CLASS;DOT_OWN_L DOT_OWN_L;DOT_OWN_R DOT_OWN_R;ONEWAY ONEWAY",
    compare_line_direction="NO_COMPARE_DIRECTION")

print("finished dfc at: " + time.strftime("%c"))

#: join the source datasets to the detect feature change output
arcpy.env.qualifiedFieldNames = False
#: Make a feature layers from the feature classes
arcpy.MakeFeatureLayer_management(current_update_fc, "current_update_roads_lyr")
arcpy.MakeFeatureLayer_management(snapshot_base_fc, "snapshot_base_roads_lyr")
arcpy.MakeFeatureLayer_management(dfc_output_fc, "output_dfc_additions_lyr", "CHANGE_TYPE not in ('NC','D')")

#: set up join fields
joinField_current_roads = arcpy.Describe("current_update_roads_lyr").OIDFieldName
joinField_snapshot_roads = arcpy.Describe("snapshot_base_roads_lyr").OIDFieldName
#joinField_dfc = "UPDATE_FID"


#: get the additions
print("begin joining additions at: " + time.strftime("%c"))
#: join the current utrans roads to the dfc table to get the new changes
arcpy.AddJoin_management("current_update_roads_lyr", joinField_current_roads, "output_dfc_additions_lyr", "UPDATE_FID")

#: select the additions
expression = r"dfc_output_fc.CHANGE_TYPE not in ('NC','D')"
layerName = "current_update_roads_lyr"
arcpy.SelectLayerByAttribute_management(layerName, "NEW_SELECTION", expression)

# copy the selected features to a new permanent feature class - the additions from the change detection
print("add additions to new fc at: " + time.strftime("%c"))
additions_fc = dirname + "\\utrans_road_changes_additions"
arcpy.CopyFeatures_management(layerName, additions_fc)


#: get the deletions
print("begin joining deletions at: " + time.strftime("%c"))
arcpy.MakeFeatureLayer_management(dfc_output_fc, "output_dfc_deletions_lyr", "CHANGE_TYPE = 'D'")
#: copy the selected features to the new feature class - the deletions from the change detection
#: join the snapshot roads to the dfc table to get the deletions
arcpy.AddJoin_management("snapshot_base_roads_lyr", joinField_snapshot_roads, "output_dfc_deletions_lyr", "BASE_FID")

#: select the deletions
expression = r"dfc_output_fc.CHANGE_TYPE = 'D'"
layerName = "snapshot_base_roads_lyr"
arcpy.SelectLayerByAttribute_management(layerName, "NEW_SELECTION", expression)

# copy the selected features to a new permanent feature class - the deletions from the change detection
print("add deletions to new fc at: " + time.strftime("%c"))
deletions_fc = dirname + "\\utrans_road_changes_deletions"
arcpy.CopyFeatures_management(layerName, deletions_fc)

#: combine the additions and deletions layers into a new fc named utrans_road_changes
print("merge the additions and deletions layers to gether into a combined output feature class: " + time.strftime("%c"))
utrans_road_changes = arcpy.Merge_management([additions_fc, deletions_fc], dirname + "\\utrans_road_changes", "", "NO_SOURCE_INFO")


#: begin section to track and report what specific fields have different field values - the dfc only reports that there was an attribute change, and doesn't indicate which field.
#: add the following fields to the utrans_roads_changes feature class: [UNIQUE_ID_chg, COUNTY_chg, DOT_RTNAME_chg, DOT_SRFTYP_chg, DOT_CLASS_chg, DOT_OWN_chg, ONEWAY_chg]
print("add the change fields at: " + time.strftime("%c"))
arcpy.management.AddFields(
    utrans_road_changes, 
    [['UNIQUEID_chg', 'TEXT', 'UniqueID change', 5, "False", ''],
     ['COUNTY_ID_chg', 'TEXT', 'CountyID change', 5, "False", ''],
     ['DOT_RTNAME_chg', 'TEXT', 'RtName change', 5, "False", ''],
     ['DOT_SRFTYP_chg', 'TEXT', 'SrfTyp change', 5, "False", ''],
     ['DOT_CLASS_chg', 'TEXT', 'DOT_Class change', 5, "False", ''],
     ['DOT_OWN_chg', 'TEXT', 'DOT_OWN change', 5, "False", ''],
     ['ONEWAY_chg', 'TEXT', 'Oneway change', 5, "False", '']])

print("begin assiging the True value to Changed fields that had changes: " + time.strftime("%c"))
#: loop through the attribute ('A') and spatial/attribute ('SA') records in the combined layer and compare values with the original values to see what fields have change
#:            0           1            2          3           4           5              6             7           8            9           10          11             12             13                  14                15              16             17
fields = ['BASE_FID','UPDATE_FID','UNIQUE_ID', 'COUNTY_L', 'COUNTY_R', 'DOT_RTNAME', 'DOT_SRFTYP', 'DOT_CLASS', 'DOT_OWN_L', 'DOT_OWN_R', 'ONEWAY', 'UNIQUEID_chg', 'COUNTY_ID_chg', 'DOT_RTNAME_chg', 'DOT_SRFTYP_chg', 'DOT_CLASS_chg', 'DOT_OWN_chg', 'ONEWAY_chg']
base_fc_oid_field_name = arcpy.Describe(snapshot_base_fc).OIDFieldName
where_clause = "CHANGE_TYPE in ('A', 'SA')"
# loop through each row in the search cursor
with arcpy.da.UpdateCursor(utrans_road_changes, fields, where_clause) as update_cursor:
    for update_row in update_cursor:

        #: get the update/current field values.
        update_fid = str(update_cursor[1])
        current_uniqueid = str(update_cursor[2])
        current_countyL = str(update_cursor[3])
        current_countyR = str(update_cursor[4])
        current_dotrtname = str(update_cursor[5])
        current_srftype = str(update_cursor[6])
        current_class = str(update_cursor[7])
        current_ownL = str(update_cursor[8])
        current_ownR = str(update_cursor[9])
        current_oneway = str(update_cursor[10])

        #: get the base/snapshot fc field values.
        base_fid = str(update_cursor[0])
        base_uniqueid = ""
        base_countyL = ""
        base_countyR = ""
        base_dotrtname = ""
        base_srftype = ""
        base_class = ""
        base_ownL = ""
        base_ownR = ""
        base_oneway = ""
        #:                 0            1           2           3             4            5              6           7           8 
        base_fields = ['UNIQUE_ID', 'COUNTY_L', 'COUNTY_R', 'DOT_RTNAME', 'DOT_SRFTYP', 'DOT_CLASS', 'DOT_OWN_L', 'DOT_OWN_R', 'ONEWAY']
        base_where_clause = str(base_fc_oid_field_name) + " = " + str(base_fid)
        with arcpy.da.SearchCursor(snapshot_base_fc, base_fields, base_where_clause) as base_search_cursor:
            for base_row in base_search_cursor:
                base_uniqueid = str(base_row[0])
                base_countyL = str(base_row[1])
                base_countyR = str(base_row[2])
                base_dotrtname = str(base_row[3])
                base_srftype = str(base_row[4])
                base_class = str(base_row[5])
                base_ownL = str(base_row[6])
                base_ownR = str(base_row[7])
                base_oneway = str(base_row[8])

        #: compare the base and update field values to see what fields have changed, and then update the "changed" fields if the values do not match.
        if current_uniqueid != base_uniqueid:
            update_row[11] = "True"
        if current_countyL != base_countyL:
            update_row[12] = "True"
        if current_countyR != base_countyR:
            update_row[12] = "True"
        if current_dotrtname != base_dotrtname:
            update_row[13] = "True"
        if current_srftype != base_srftype:
            update_row[14] = "True"
        if current_class != base_class:
            update_row[15] = "True"
        if current_ownL != base_ownL:
            update_row[16] = "True"
        if current_ownR != base_ownR:
            update_row[16] = "True"
        if current_oneway != base_oneway:
            update_row[17] = "True"

        update_cursor.updateRow(update_row)

#: done!
print("finished script at: " + time.strftime("%c"))