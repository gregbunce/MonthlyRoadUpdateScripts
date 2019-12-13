#KG Yo
#2/9/2015

#Update UDOT data layers in the SGID

# *** Make sure to update the folder name before running! ***

import arcpy, os

udotGDB = 'C:\\Users\\gbunce\\Documents\\projects\\DataForGDrive\\non_road_update_uploads\\2019_12_02\\UDOTRoutes_LRS.gdb\\'  # UNCOMMENT LRS CODE IF YOU WANT TO UPDATE THAT FC, TOO
sgidSDE = 'Database Connections\\Transportation@SGID@internal.agrc.utah.gov.sde\\'

udotMP = "UDOT_Mileposts"
udotLRS = "UDOTRoutes_LRS"
udot10th = "UDOTTenth_Mpts"

##sgidMP = "sgidMP"
##sgidLRS = "sgidLRS"
##sgid10th = "sgid10thMP"

sgidMP = "SGID.TRANSPORTATION.UDOTMileposts"
sgidLRS = "SGID.TRANSPORTATION.UDOTRoutes_LRS"
sgid10th = "SGID.TRANSPORTATION.UDOTTenthMileRefPoints"

arcpy.DeleteFeatures_management(sgidSDE + sgidMP)
print "sgidMP Features Deleted"

arcpy.DeleteFeatures_management(sgidSDE + sgidLRS)
print "sgidLRS Features Deleted"

arcpy.DeleteFeatures_management(sgidSDE + sgid10th)
print "sgid10thMP Features Deleted"

arcpy.Append_management(udotGDB + udotMP, sgidSDE + sgidMP, "NO_TEST", "", "")
print "udotMP appended"
arcpy.Append_management(udotGDB + udotLRS, sgidSDE +  sgidLRS, "NO_TEST", "", "")
print "udotLRS appended"
arcpy.Append_management(udotGDB + udot10th, sgidSDE + sgid10th, "NO_TEST", "", "")
print "udot10th appended"

print "update complete!"