'''
Created on Dec 20, 2012

@author: kwalker
'''
import arcpy, os

#arcpy.env.overwriteOutput = True


utransSource = arcpy.GetParameterAsText(0)
#utransSource = r"C:\KW_Working\Other\kellysScript\testUtrans.gdb\StateWideStreets"
sgidTarget = arcpy.GetParameterAsText(1)
#sgidTarget = r"C:\KW_Working\Other\kellysScript\testSGID.gdb\Roads"
#restrictedFields = ["CLASS", "COLLDATE", "ACCURACY", "SOURCE", "NOTES", "DSTRBWIDTH", "LOCALFUNC", "MAINTJURIS", "STATUS" , "ACCESS", "USAGENOTES"]
#restrictedFields = ["ADDR_SYS", "CARTOCODE"]
restrictedFields = [""]

arcpy.env.workspace = "in_memory"
utransFeature = "UtransFeature"

arcpy.DeleteFeatures_management(sgidTarget)
arcpy.AddMessage("SGID Road Features Deleted")

#arcpy.MakeFeatureLayer_management(utransSource, "utrans_lyr")
arcpy.MakeFeatureLayer_management(utransSource, "utrans_lyr", "CARTOCODE <> '99'")

testFC = arcpy.CopyFeatures_management("utrans_lyr", utransFeature)
print "Copied into Memory"
arcpy.AddMessage("Copied into Memory")
#arcpy.DeleteField_management(utransFeature, restrictedFields)

##utransFields = arcpy.ListFields(utransFeature)
##for f in utransFields:
##    if restrictedFields.count(f.baseName) > 0:
##        print "delete failed"
##        arcpy.AddError("Restricted Field Error")

arcpy.Append_management(utransFeature, sgidTarget, "NO_TEST")
print "Completed"
arcpy.Delete_management(utransFeature)
arcpy.AddMessage("Completed")
