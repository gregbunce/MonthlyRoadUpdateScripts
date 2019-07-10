import arcpy
import inspect
 
arcpy.env.workspace = r'C:\temp\ETLs_ForCounties\CarbonCountyRoads.gdb'
 
#functions to remove null string or integer and replace with '' or 0
def RemoveNullString(x):
    if x is None:
        return ''
    else:
        return x
 
def RemoveNullInt(y):
    if y is None:
        return 0
    else:
        return y
 
def formatFeatureClass(FC):
    inspect.getsource(RemoveNullString)
    inspect.getsource(RemoveNullInt)
    ##format string fields
    #arcpy.CalculateField_management(FC,"District","RemoveNullString(!District!)","PYTHON_9.3")
    #arcpy.CalculateField_management(FC,"Species","RemoveNullString(!Species!)","PYTHON_9.3")
 
    ##format Numeric Fields
    #arcpy.CalculateField_management(FC,"Area","RemoveNullInt(!Area!)","PYTHON_9.3")
    #arcpy.CalculateField_management(FC,"Harvested","RemoveNullInt(!Harvested!)","PYTHON_9.3")
    #arcpy.CalculateField_management(FC,"Non","RemoveNullInt(!Non!)","PYTHON_9.3")
    #arcpy.CalculateField_management(FC,"NR","RemoveNullInt(!NR!)","PYTHON_9.3")
    #arcpy.CalculateField_management(FC,"Resident","RemoveNullInt(!Resident!)","PYTHON_9.3")
    #arcpy.CalculateField_management(FC,"Total","RemoveNullInt(!Total!)","PYTHON_9.3")

    # for carbon county's requested etl
    arcpy.CalculateField_management(FC,"SUF_DIR","RemoveNullString(!SUF_DIR!)", "PYTHON", str(inspect.getsource(RemoveNullString)))
    arcpy.CalculateField_management(FC,"ALIAS1","RemoveNullString(!ALIAS1!)","PYTHON", str(inspect.getsource(RemoveNullString)))
    arcpy.CalculateField_management(FC,"ALIAS1_TYP","RemoveNullString(!ALIAS1_TYP!)","PYTHON", str(inspect.getsource(RemoveNullString)))
    arcpy.CalculateField_management(FC,"ALIAS2","RemoveNullString(!ALIAS2!)","PYTHON", str(inspect.getsource(RemoveNullString)))
    arcpy.CalculateField_management(FC,"ALIAS2_TYP","RemoveNullString(!ALIAS2_TYP!)","PYTHON", str(inspect.getsource(RemoveNullString)))
    arcpy.CalculateField_management(FC,"S_NAME","RemoveNullString(!S_NAME!)","PYTHON", str(inspect.getsource(RemoveNullString)))
    arcpy.CalculateField_management(FC,"PRE_DIR","RemoveNullString(!PRE_DIR!)","PYTHON", str(inspect.getsource(RemoveNullString)))
    arcpy.CalculateField_management(FC,"S_TYPE","RemoveNullString(!S_TYPE!)","PYTHON", str(inspect.getsource(RemoveNullString)))
    arcpy.CalculateField_management(FC,"ACS_ALIAS","RemoveNullString(!ACS_ALIAS!)","PYTHON", str(inspect.getsource(RemoveNullString)))

    arcpy.CalculateField_management(FC,"SPD_LMT","RemoveNullInt(!SPD_LMT!)","PYTHON", str(inspect.getsource(RemoveNullInt)))
    arcpy.CalculateField_management(FC,"L_F_ADD","RemoveNullInt(!L_F_ADD!)","PYTHON", str(inspect.getsource(RemoveNullInt)))
    arcpy.CalculateField_management(FC,"L_T_ADD","RemoveNullInt(!L_T_ADD!)","PYTHON", str(inspect.getsource(RemoveNullInt)))
    arcpy.CalculateField_management(FC,"R_F_ADD","RemoveNullInt(!R_F_ADD!)","PYTHON", str(inspect.getsource(RemoveNullInt)))
    arcpy.CalculateField_management(FC,"R_T_ADD","RemoveNullInt(!R_T_ADD!)","PYTHON", str(inspect.getsource(RemoveNullInt)))



 
 
Features = arcpy.ListFeatureClasses()
 
for fc in Features:
    print "Formatting: " + fc
    formatFeatureClass(fc)
 
print "Scripting Complete"