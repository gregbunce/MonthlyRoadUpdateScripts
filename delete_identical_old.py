import arcpy, os

#: use arcgis pro python 3

#: delete identical roads
arcpy.DeleteIdentical_management(in_dataset="C:/Temp/RoadGrinder.gdb/GeocodeRoads", fields="Shape;ADDRSYS_L;ADDRSYS_R;FROMADDR_L;TOADDR_L;FROMADDR_R;TOADDR_R;PREDIR;NAME;POSTTYPE;POSTDIR;ZIPCODE_L;ZIPCODE_R;GLOBALID_SGID;Shape_Length", xy_tolerance="", z_tolerance="0")

#: delete identical alt names address points table
arcpy.DeleteIdentical_management(in_dataset="C:/Temp/RoadGrinder.gdb/AtlNamesAddrPnts", fields="AddSystem;AddNum;AddNumSuffix;PrefixDir;StreetName;StreetType;SuffixDir;ZipCode;UnitType;UnitID;City;CountyID;UTAddPtID", xy_tolerance="", z_tolerance="0")

#: delete identical alt names roads table
arcpy.DeleteIdentical_management(in_dataset="C:/Temp/RoadGrinder.gdb/AtlNamesRoads", fields="ADDRSYS_L;ADDRSYS_R;FROMADDR_L;TOADDR_L;FROMADDR_R;TOADDR_R;PREDIR;NAME;POSTTYPE;POSTDIR;ZIPCODE_L;ZIPCODE_R;GLOBALID_SGID", xy_tolerance="", z_tolerance="0")

print("done")