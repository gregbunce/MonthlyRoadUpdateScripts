#Update UDOT data layers in the SGID


# *** READ ME FIRST ***
# Make sure to update the folder name before running
# Make sure the field schemas match as we are using "NO TEST"
# UNCOMMENT the layers that you don't want updated and don't forget to uncomment the delete and append sections
# note: if you get an error, it might be b/c the layer names don't match.  change the names in the fgdb to match sgid


import arcpy, os

udotGDB = 'C:\\Users\\gbunce\\Documents\\projects\\UTRANS\\MonthlyUDOT_DataUpdates\\UDOT_LRS_Feb22_2019.gdb\\UDOTRoutes_LRS\\'
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