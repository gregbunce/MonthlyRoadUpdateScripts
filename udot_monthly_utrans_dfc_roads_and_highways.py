#: use python 3

# Import system modules
import os
import arcpy
from arcpy import env
import time

#: set the input datasets
current_update_fc = 'C:\\Users\\gbunce\\Documents\\projects\\UTRANS\\udot_monthly_change_detection\\script_testing\\udot_dfc_testing.gdb\\update_fc'
snapshot_base_fc = 'C:\\Users\\gbunce\\Documents\\projects\\UTRANS\\udot_monthly_change_detection\\script_testing\\udot_dfc_testing.gdb\\base_fc'

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
arcpy.Merge_management([additions_fc, deletions_fc], dirname + "\\utrans_road_changes", "", "NO_SOURCE_INFO")

#: loop through the attribute and spatial/attribute records in the combined layer and compare values with the original values to see what fields have change


#: done!
print("finished script at: " + time.strftime("%c"))
