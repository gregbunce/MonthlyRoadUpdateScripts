import arcpy
import datetime
import time
import os
#from datetime import date
#from datetime import datetime

# get the date
#today = date.today()
#strDate = str(today.month).zfill(2) + str(today.day).zfill(2) +  str(today.year) 

sgid_roads = r"Database Connections\DC_agrc@SGID10@sgid.agrc.utah.gov.sde\SGID10.TRANSPORTATION.Roads"

# main function
def main():

    #### Create a folder based on the date (ie: Year_Month_Day = 2018_4_16)
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    folder_name = str(year) + "_" + str(month) + "_" + str(day)
    # create the folder
    print "Creating Directory..."
    directory = "D:/NetworkDataset/RecentBuilds_forWebsite/" + folder_name
    if not os.path.exists(directory):
        print "Creating Directory: " + str(directory) + " ..."
        os.makedirs(directory)
    else:
        print "Directory: " + str(directory) + " exists."



    # create new fgdb
    print "Creating File Geodatabase..."
    network_fgdb = arcpy.CreateFileGDB_management(directory, 'UtahRoadsNetworkAnalysis.gdb')

    # create dataset in the fgdb
    print "Creating Feature Dataset..."
    arcpy.CreateFeatureDataset_management(network_fgdb, 'NetworkDataset', sgid_roads)

    # import the sgid roads fc
    print "Importing SGID Roads ..."
    expression = "ZIPCODE_L = '84763'" ##TESTING STUFF##
    network_roads = arcpy.FeatureClassToFeatureClass_conversion(sgid_roads, str(network_fgdb) + r'/NetworkDataset', 'Roads', expression)

    # add the needed fields
    print "Add needed network fields to fgdb road data"
    arcpy.AddField_management(network_roads,"NETSUBTYPE", "SHORT", "","","")
    arcpy.AddField_management(network_roads,"USEEXIST", "TEXT", "","","1")
    arcpy.AddField_management(network_roads,"URBTRAFFIC", "TEXT", "","","1")
    arcpy.AddField_management(network_roads,"EXCL_WALK", "TEXT", "","","1")
    arcpy.AddField_management(network_roads,"IMPED_MIN","DOUBLE","6","2")
    arcpy.AddField_management(network_roads,"F_T_IMP_MIN","DOUBLE","6","2")
    arcpy.AddField_management(network_roads,"T_F_IMP_MIN","DOUBLE","6","2")
    arcpy.AddField_management(network_roads,"IMPED_PED","DOUBLE","6","2")
    #arcpy.AddField_management(network_roads,"STARTX","DOUBLE","7","1")
    #arcpy.AddField_management(network_roads,"ENDX","DOUBLE","7","1")
    #arcpy.AddField_management(network_roads,"STARTY","DOUBLE","7","1")
    #arcpy.AddField_management(network_roads,"ENDY","DOUBLE","7","1")

    # but, do this for only limited access roads
    arcpy.MakeFeatureLayer_management(network_roads, 'network_roads_lyr', "DOT_HWYNAM <> ''")
    arcpy.AddGeometryAttributes_management('network_roads_lyr', "LINE_START_MID_END")
    arcpy.Delete_management('network_roads_lyr')
    #arcpy.CalculateGeometryAttributes_management(network_roads, [["STARTX", "LINE_START_X"], ["ENDX", "LINE_END_X"]])


    # create the needed scratch data (ie: the urban areas) and assign the 
    urban_areas = generate_scratch_data(directory)   
    #arcpy.MakeFeatureLayer_management(urban_areas, 'urban_areas_lyr')
    arcpy.MakeFeatureLayer_management(network_roads, 'network_roads_lyr')
    urban_roads_selected = arcpy.SelectLayerByLocation_management('network_roads_lyr', 'intersect', urban_areas)
    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
    arcpy.CalculateField_management(urban_roads_selected, field="URBTRAFFIC", expression='"Y"', expression_type='VB', code_block='')
    # calculte the segments that were not in an urban area to "N"
    urban_roads_selected = arcpy.SelectLayerByAttribute_management('network_roads_lyr','NEW_SELECTION', "URBTRAFFIC is NULL")
    arcpy.CalculateField_management(urban_roads_selected, field="URBTRAFFIC", expression='"N"', expression_type='VB', code_block='')
    arcpy.Delete_management('network_roads_lyr')


    ## create a feature class in the fgdb
    #network_roads = arcpy.CreateFeatureclass_management(network_fgdb, "Roads", "POLYLINE", 
    #                                    'D:/NetworkDataset/networkdataset_roads_template.gdb/Roads_template', "DISABLED", "DISABLED", 
    #                                    sgid_roads)

    ## TO DO ##
    # calculate geometry on the start/end x/y fields


    # import the roads into network dataset
    ## import_RoadsIntoNetworkDataset(sgid_roads, network_roads)



# this function imports the user-defined utrans roads into the the netork dataset feature class 
def import_RoadsIntoNetworkDataset(sgid_roads_to_import, network_roads):    
    # get list of field names
    sgid_roads_fieldnames = [f.name for f in arcpy.ListFields(sgid_roads_to_import)]
    network_roads_fieldnames = [f.name for f in arcpy.ListFields(network_roads)]

    # set up search cursors to select and insert data between feature classes (define two cursor on next line: search_cursor and insert_cursor)
    with arcpy.da.SearchCursor(sgid_roads_to_import, '*', sql_clause=('TOP 10', None)) as search_cursor, arcpy.da.InsertCursor(network_roads, network_roads_fieldnames) as insert_cursor:
        # itterate though the intersected utrans road centerline features
        for utrans_row in search_cursor:
            name = str(search_cursor[sgid_roads_fieldnames.index('NAME')])
            pre_dir = str(search_cursor[sgid_roads_fieldnames.index('PREDIR')])


            # create list of row values to insert (maybe just use the "network_roads_fieldnames" list)
            insert_row_values = [name, pre_dir]
            # insert the new row with the list of values
            for insert_row in insert_row_values:
                insert_cursor.insertRow(insert_row) 



def generate_scratch_data(directory):
    # create new fgdb
    print "Creating Scratch File Geodatabase..."
    network_fgdb = arcpy.CreateFileGDB_management(directory, 'NetworkBuild_scratchData.gdb')

    # union the census urban areas and the sgid muni
    print "Union the Census Urban Areas and SGID Munis"
    unioned_fc = arcpy.Union_analysis(in_features="'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.DEMOGRAPHIC.UrbanAreasCensus2010' #;'Database Connections/DC_agrc@SGID10@sgid.agrc.utah.gov.sde/SGID10.BOUNDARIES.Municipalities' #", out_feature_class= str(directory) + "/NetworkBuild_scratchData.gdb/UrbanAreasMuni_Union", join_attributes="ONLY_FID", cluster_tolerance="", gaps="GAPS")

    # dissolve this unioned data
    print "Dissolve the unioned layer"
    return arcpy.Dissolve_management(in_features=unioned_fc, out_feature_class= str(directory) + "/NetworkBuild_scratchData.gdb/UrbanAreasMuni_Union_Dissolved", dissolve_field="", statistics_fields="", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")


if __name__ == "__main__":
    # execute only if run as a script
    main()

