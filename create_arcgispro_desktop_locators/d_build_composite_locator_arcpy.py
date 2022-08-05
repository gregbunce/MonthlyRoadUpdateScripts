import arcpy
arcpy.geocoding.CreateCompositeAddressLocator(r"C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_address_point_locator.loc address_points;C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_roads_locator.loc roads", r'Address "Address or Place" true true false 100 Text 0 0,First,#,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_address_point_locator.loc,Address,0,0,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_roads_locator.loc,Address,0,0;Address2 "Address2" true true false 100 Text 0 0,First,#,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_address_point_locator.loc,Address2,0,0,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_roads_locator.loc,Address2,0,0;Address3 "Address3" true true false 100 Text 0 0,First,#,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_address_point_locator.loc,Address3,0,0,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_roads_locator.loc,Address3,0,0;Neighborhood "Neighborhood" true true false 50 Text 0 0,First,#,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_address_point_locator.loc,Neighborhood,0,0,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_roads_locator.loc,Neighborhood,0,0;City "City" true true false 50 Text 0 0,First,#,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_address_point_locator.loc,City,0,0,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_roads_locator.loc,City,0,0;Subregion "County" true true false 50 Text 0 0,First,#,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_address_point_locator.loc,Subregion,0,0,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_roads_locator.loc,Subregion,0,0;Region "State" true true false 50 Text 0 0,First,#,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_address_point_locator.loc,Region,0,0,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_roads_locator.loc,Region,0,0;Postal "ZIP" true true false 20 Text 0 0,First,#,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_address_point_locator.loc,Postal,0,0,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_roads_locator.loc,Postal,0,0;PostalExt "ZIP4" true true false 20 Text 0 0,First,#,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_address_point_locator.loc,PostalExt,0,0,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_roads_locator.loc,PostalExt,0,0;CountryCode "Country" true true false 100 Text 0 0,First,#,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_address_point_locator.loc,CountryCode,0,0,C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_roads_locator.loc,CountryCode,0,0', "address_points #;roads #", r"C:\Users\gbunce\Documents\projects\RebuildAddressLocators\ugrc_composite_locator")