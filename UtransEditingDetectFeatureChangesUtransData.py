# Name:        UtransEditingDetectFeatureChanges.py
# Description: Perform change detection between newly received road data and
#              existing road data and find the number of new roads and the
#              total length of them.
# Author:      gbunce
# -----------------------------------------------------------------------

# NOTE
### three ### pound signs indicates that the user needs to change a variable before running this code

# Import system modules
import os
import arcpy
from arcpy import env
import time

# Set environment settings
env.overwriteOutput = True
#env.workspace = r"D:\UTRANS\Updates\SummitCenterlines_16_02_17.gdb" ### change database name ###


# Set local variables
updateFeatures = arcpy.GetParameterAsText(0)
baseFeatures = arcpy.GetParameterAsText(1)
#updateFeatures = "SummitUTDM_RecentEditsDefQuery_05262016" ### change fc name ###
#baseFeatures = "SummitSGID_05262016" ### change fc name ###

dirname = os.path.dirname(arcpy.Describe(updateFeatures).catalogPath)
desc = arcpy.Describe(dirname)
if hasattr(desc, "datasetType") and desc.datasetType=='FeatureDataset':
    dirname = os.path.dirname(dirname)

#dfcOutput = "DFC_RESULT"
#dfcResult = arcpy.Describe(updateFeatures).catalogPath + "\\DFC_RESULT"
#dfcOutput = arcpy.Describe(updateFeatures).catalogPath + "\\DFC_RESULT"
dfcOutput = dirname + "\\DFC_RESULT"


# get the expression for the query def
if arcpy.GetParameterAsText(2) == "Beaver":
    expresstion = "COUNTY_L = '49001' or COUNTY_R = '49001'"
if arcpy.GetParameterAsText(2) == "Box Elder":
    expresstion = "COUNTY_L = '49003' or COUNTY_R = '49003'"
if arcpy.GetParameterAsText(2) == "Cache":
    expresstion = "COUNTY_L = '49005' or COUNTY_R = '49005'"
if arcpy.GetParameterAsText(2) == "Carbon":
    expresstion = "COUNTY_L = '49007' or COUNTY_R = '49007'"
if arcpy.GetParameterAsText(2) == "Daggett":
    expresstion = "COUNTY_L = '49009' or COUNTY_R = '49009'"
if arcpy.GetParameterAsText(2) == "Davis":
    expresstion = "COUNTY_L = '49011' or COUNTY_R = '49011'"
if arcpy.GetParameterAsText(2) == "Duchesne":
    expresstion = "COUNTY_L = '49013' or COUNTY_R = '49013'"
if arcpy.GetParameterAsText(2) == "Emery":
    expresstion = "COUNTY_L = '49015' or COUNTY_R = '49015'"
if arcpy.GetParameterAsText(2) == "Garfield":
    expresstion = "COUNTY_L = '49017' or COUNTY_R = '49017'"
if arcpy.GetParameterAsText(2) == "Grand":
    expresstion = "COUNTY_L = '49019' or COUNTY_R = '49019'"
if arcpy.GetParameterAsText(2) == "Iron":
    expresstion = "COUNTY_L = '49021' or COUNTY_R = '49021'"
if arcpy.GetParameterAsText(2) == "Juab":
    expresstion = "COUNTY_L = '49023' or COUNTY_R = '49023'"
if arcpy.GetParameterAsText(2) == "Kane":
    expresstion = "COUNTY_L = '49025' or COUNTY_R = '49025'"
if arcpy.GetParameterAsText(2) == "Millard":
    expresstion = "COUNTY_L = '49027' or COUNTY_R = '49027'"
if arcpy.GetParameterAsText(2) == "Morgan":
    expresstion = "COUNTY_L = '49029' or COUNTY_R = '49029'"
if arcpy.GetParameterAsText(2) == "Piute":
    expresstion = "COUNTY_L = '49031' or COUNTY_R = '49031'"
if arcpy.GetParameterAsText(2) == "Rich":
    expresstion = "COUNTY_L = '49033' or COUNTY_R = '49033'"
if arcpy.GetParameterAsText(2) == "Salt Lake":
    #expresstion = "COUNTY_L = '49035' and USPS_PLACE = 'SOUTH JORDAN'"
    expresstion = "COUNTY_L = '49035' or COUNTY_R = '49035'"
if arcpy.GetParameterAsText(2) == "San Juan":
    expresstion = "COUNTY_L = '49037' or COUNTY_R = '49037'"
if arcpy.GetParameterAsText(2) == "Sanpete":
    expresstion = "COUNTY_L = '49039' or COUNTY_R = '49039'"
if arcpy.GetParameterAsText(2) == "Sevier":
    expresstion = "COUNTY_L = '49041' or COUNTY_R = '49041'"
if arcpy.GetParameterAsText(2) == "Summit":
    expresstion = "COUNTY_L = '49043' or COUNTY_R = '49043'"
if arcpy.GetParameterAsText(2) == "Tooele":
    expresstion = "COUNTY_L = '49045' or COUNTY_R = '49045'"
if arcpy.GetParameterAsText(2) == "Uintah":
    expresstion = "COUNTY_L = '49047' or COUNTY_R = '49047'"
if arcpy.GetParameterAsText(2) == "Utah":
    expresstion = "COUNTY_L = '49049' or COUNTY_R = '49049'"
if arcpy.GetParameterAsText(2) == "Wasatch":
    expresstion = "COUNTY_L = '49051' or COUNTY_R = '49051'"
if arcpy.GetParameterAsText(2) == "Washington":
    expresstion = "COUNTY_L = '49053' or COUNTY_R = '49053'"
if arcpy.GetParameterAsText(2) == "Wayne":
    expresstion = "COUNTY_L = '49055' or COUNTY_R = '49055'"
if arcpy.GetParameterAsText(2) == "Weber":
    expresstion = "COUNTY_L = '49057' or COUNTY_R = '49057'"
if arcpy.GetParameterAsText(2) == "Uinta":
    expresstion = "COUNTY_L = '56041' or COUNTY_R = '56041'"

arcpy.AddMessage("expression name: " + expresstion)


arcpy.Delete_management("baseFeatureCoQueryDef")
arcpy.MakeFeatureLayer_management(arcpy.GetParameterAsText(1), "baseFeatureCoQueryDef", expresstion)


search_distance = "50" # 300 feet is about 90 meters \ 40 meters = 131.234 feet
#search_distance = "200 Feet" # The distance used to search for match candidates. A distance must be specified and it must be greater than zero. You can choose a preferred unit; the default is the feature unit.
match_fields = "NAME NAME"
statsTable = arcpy.Describe(updateFeatures).catalogPath + "\\new_roads_stats"
#change_tolerance = "300 Feet"
change_tolerance = "50"
#change_tolerance = "40" # The Change Tolerance serves as the width of a buffer zone around the update features or the base features.  It's the distance used to determine if there is a spatial change. All matched update features and base features are checked against this tolerance. If any portions of update or base features fall outside the zone around the matched feature, it is considered a spatial change.

## without alias values
## with alias values
#compare_fields = "PREDIR PREDIR; NAME NAME; POSTDIR POSTDIR; FROMADDR_L FROMADDR_L; TOADDR_L TOADDR_L; FROMADDR_R FROMADDR_R; TOADDR_R TOADDR_R; AN_NAME AN_NAME; AN_POSTDIR AN_POSTDIR"
compare_fields = "PREDIR PREDIR; POSTTYPE POSTTYPE; NAME NAME; POSTDIR POSTDIR; FROMADDR_L FROMADDR_L; TOADDR_L TOADDR_L; FROMADDR_R FROMADDR_R; TOADDR_R TOADDR_R; A1_PREDIR A1_PREDIR; A1_NAME A1_NAME; A1_POSTTYPE A1_POSTTYPE; A1_POSTDIR A1_POSTDIR; A2_PREDIR A2_PREDIR; A2_NAME A2_NAME; A2_POSTTYPE A2_POSTTYPE; A2_POSTDIR A2_POSTDIR; AN_NAME AN_NAME; AN_POSTDIR AN_POSTDIR"
#compare_fields = "PREDIR PREDIR; POSTTYPE POSTTYPE; NAME NAME; POSTDIR POSTDIR; FROMADDR_L FROMADDR_L; TOADDR_L TOADDR_L; FROMADDR_R FROMADDR_R; TOADDR_R TOADDR_R; AN_NAME AN_NAME; AN_POSTDIR AN_POSTDIR";

arcpy.AddMessage("Begining detect feature change process...")
#print "begining detect feature change process..."
# Perform spatial change detection
arcpy.DetectFeatureChanges_management(updateFeatures, "baseFeatureCoQueryDef", dfcOutput, search_distance, match_fields, statsTable, change_tolerance, compare_fields)
#print "finished detect feature change process!"
arcpy.AddMessage("Finished detect feature change process.")


#print "begining adding CURRENT_NOTES and PREV__NOTES fields..."
arcpy.AddMessage("Begin adding notes fields...")
arcpy.AddField_management(dfcOutput, 'CURRENT_NOTES', 'TEXT', '','', 50, 'DfcCurNotes')
arcpy.AddField_management(dfcOutput, 'PREV__NOTES', 'TEXT', '','', 50, 'DfcPrevNotes')
arcpy.AddField_management(dfcOutput, 'EDITOR', 'TEXT', '','', 20, 'Editor')
arcpy.AddField_management(dfcOutput, 'EDIT_DATE', 'DATE', '','', '', 'EditDate')
arcpy.AddField_management(dfcOutput, 'DATE_ADDED', 'DATE', '','', '', 'DateAdded')
arcpy.AddField_management(dfcOutput, 'COFIPS', 'TEXT', '','', 5, 'County')

## update the date added field with today's date and the copfips field with the county number
strTimeNow = time.strftime("%c")
strCountyNumber = expresstion[-6:-1]
fields = ['DATE_ADDED', 'COFIPS']

with arcpy.da.UpdateCursor(dfcOutput, fields) as cursor:
        for row in cursor:
            row[0] = strTimeNow
            row[1] = strCountyNumber
            cursor.updateRow(row)

arcpy.AddMessage("Begin changing feature class alias name...")
# add alias name to the feature class for use in the ArcMap Utrans Editor
arcpy.AlterAliasName(dfcOutput, "DFC_RESULT")


## append the new rows to dfc on sde
arcpy.MakeFeatureLayer_management(dfcOutput, "dfcOutput_DefQueryLyr","CHANGE_TYPE NOT IN ('NC','D')")
outLocation = r"Database Connections\DC_TRANSADMIN@UTRANS@utrans.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Centerlines_Edit\UTRANS.TRANSADMIN.DFC_RESULT"
schemaType = "NO_TEST"
fieldMappings = ""
subtype = ""
arcpy.Append_management("dfcOutput_DefQueryLyr", outLocation, schemaType, fieldMappings, subtype)