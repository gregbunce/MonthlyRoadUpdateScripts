#KG Yo
#2/9/2015

#Update UDOT data layers in the SGID

# *** Make sure to update the folder name before running! ***

import arcpy, os

udotGDB = 'D:\\UTRANS\MonthlyUDOT_DataUpdates\\UDOT_LRS_Feb22_2019.gdb\\'  # UNCOMMENT LRS CODE IF YOU WANT TO UPDATE THAT FC, TOO
sgidSDE = 'Database Connections\\DC_Transportation@sgid10@sgid.agrc.utah.gov.sde\\'

udotMP = "UDOT_Mileposts"
udotLRS = "UDOTRoutes_LRS"
udot10th = "UDOTTenth_Mpts"

##sgidMP = "sgidMP"
##sgidLRS = "sgidLRS"
##sgid10th = "sgid10thMP"

sgidMP = "SGID10.TRANSPORTATION.UDOTMileposts"
sgidLRS = "SGID10.TRANSPORTATION.UDOTRoutes_LRS"
sgid10th = "SGID10.TRANSPORTATION.UDOTTenthMileRefPoints"

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