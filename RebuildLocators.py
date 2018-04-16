#-------------------------------------------------------------------------------
# Name:        RebuildLocators.py
# Purpose:     Rebuild Address Locators
# Author:      gbunce
# Created:     04/09/2018
#-------------------------------------------------------------------------------
import arcpy
# from arcpy import env

# env.workspace = "Database Connections\SGID_Transportation@SGID10@sgid.agrc.utah.gov.sde"
# env.workspace = "D:\Rebuild Address Locators"

# Locators
AGRC_AddressPointLocator = "D:\Rebuild Address Locators\AGRC_AddressPointLocator" 
AGRC_RoadsLocator = "D:\Rebuild Address Locators\AGRC_RoadsLocator"
AGRC_CompositeLocator = "D:\Rebuild Address Locators\AGRC_CompositeLocator"

# Rebuild Locaotrs
print "start rebuilding AGRC_AddressPointLocator"
arcpy.RebuildAddressLocator_geocoding(AGRC_AddressPointLocator)
print "done rebuilding AGRC_AddressPointLocator"
print "start rebuilding AGRC_RoadsLocator"
arcpy.RebuildAddressLocator_geocoding(AGRC_RoadsLocator)
print "done rebuilding AGRC_RoadsLocator"
print "start rebuilding AGRC_CompositeLocator"
arcpy.RebuildAddressLocator_geocoding(AGRC_CompositeLocator)
print "done rebuilding AGRC_CompositeLocator"

print "done rebuilding all locators"
print "recreate the 3 locator packages and copy to K:\AGRC Projects\Locators"
print "Done!  Press any key to close."