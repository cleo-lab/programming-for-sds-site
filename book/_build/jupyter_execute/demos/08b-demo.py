#!/usr/bin/env python
# coding: utf-8

# # Vector data analysis
# 
# In the second demo of this week, we will introduce the basics of vector data analysis in Python with an example. We have two shapefiles. The first shapefile contains the name, location, and capacity of all major sports stadiums in the United States as **points**. The second shapefile contains the states on the United States as **polygons**. An alien would like to know which state contains the highest number of stadiums, the highest number of seats, and the closest and furthest stadiums from University of Oregon's campus. 

# In[211]:


import geopandas as gpd

# Import data
stadiums = gpd.read_file('data/sports_venues.shp')
states = gpd.read_file('data/us_states.shp')


# In[212]:


stadiums


# ## Explore
# 
# It is always good practice to start with a visualization to check everything is projected properly.

# In[213]:


stadiums.explore()


# In[214]:


stadiums.info()


# The `info()` method reveals that there are no missing values... or are there?

# In[215]:


stadiums.describe()


# ## Remove missing values
# 
# When we run `describe()` we notice that the **min** value is `-999` which is a value often used to indicate **no data**. Since we have no logical way of interpolating those values, we will just remove these rows. We can do this by filtring our DataFrame with a **mask** that returns `True` if values are **not equal** to `-999`.

# In[217]:


stadiums = stadiums[stadiums['CAPACITY'] != -999]
stadiums.describe()


# ## Check projections
# 
# If we are going to find how many stadiums are in each state, we will need to join the DataFrames. But we can only do this if they are in the same projection.

# In[218]:


stadiums.crs


# In[219]:


states.crs


# Since they are in different projections, we will convert the `stadiums` DataFrame to match the `states` DataFrame.

# In[220]:


stadiums = stadiums.to_crs('EPSG:5070')
stadiums.crs


# ## Join DataFrames
# 
# A spatial join ([`sjoin`](https://geopandas.org/en/stable/gallery/spatial_joins.html)) can be used to combine two `GeoDataFrames` based on the spatial relationship between their geometries. A common use case might be a spatial join between a point layer (stadiums) and a polygon layer (states) so that we we retain the point geometries and add the attributes of the intersecting polygons. 
# 
# Now we know from exploring the data that there are some stadiums that are outside the US. We would like to exclude those from our analysis. An **inner join** (`how='inner'`), keeps rows from both `GeoDataFrames` **only** when the points are contained within the polygons.

# In[221]:


stadiums_usa = stadiums.sjoin(states, how='inner')


# Now when we plot our data again, we find that there are no stadiums outside the USA and that the points have more attributes, including the **state** that they are within. 

# ````{margin}
# ```{note}
# Also notice that since the attribute `NAME` was in both datasets, `GeoPandas` automatically appends `_right` and `_left` to distinguish them.
# ```
# ````
# 

# In[222]:


stadiums_usa.explore()


# ## Compute stats
# 
# We can complete our first task by grouping the stadiums by state, summing their capacities, and sorting from highest to lowest. 

# In[224]:


stadiums_usa.groupby('NAME_right')['CAPACITY'].sum().sort_values(ascending=False).head()


# ```{note}
# Calling more than one method in an object is called **method chaining**.
# ```
# 

# In[225]:


top_state = stadiums_usa.groupby('NAME_right')['CAPACITY'].sum().sort_values(ascending=False).index[0]
top_seats = stadiums_usa.groupby('NAME_right')['CAPACITY'].sum().sort_values(ascending=False).iloc[0]

f"{top_state} has the most stadium seats in the US with {int(top_seats)}"


# If we wanted to find the state with the most stadiums we could can just change `sum()` to `count()`.

# In[226]:


stadiums_usa.groupby('NAME_right')['CAPACITY'].count().sort_values(ascending=False).head()


# In[227]:


top_state = stadiums_usa.groupby('NAME_right')['CAPACITY'].count().sort_values(ascending=False).index[0]
top_stadiums = stadiums_usa.groupby('NAME_right')['CAPACITY'].count().sort_values(ascending=False).iloc[0]

f"{top_state} has the most sports stadiums in the US with {int(top_stadiums)}"


# ## Measure distance
# 
# Our final task is to compute the distance between University of Oregon campus and all the stadiums in the dataset. 

# ```{caution}
# When computing distance or area, we must make sure that our data have a projected CRS (in meters, feet, kilometers etc.) not a geographic one (in degrees). `GeoPandas` operations are planar, whereas degrees reflect the position on a sphere. Therefore, spatial operations using degrees may not yield correct results.
# ```

# We are OK to compute distances using our stadium data because when we call the `crs` method, we can see that the Easting and Northing are in the **meters**. 

# In[234]:


stadiums_usa.crs


# We will first create a `GeoDataFrame` with a single row that represents the longitude and latitude of campus (-123.0783, 44.04505) as a `Point` data type. 

# In[229]:


from shapely.geometry import Point

data = {'geometry': [Point(-123.0783, 44.04505)]}

s = gpd.GeoDataFrame(data, crs="EPSG:4326")
s


# Next we must convert this `GeoDataFrame` to the same projection as our stadium data (`EPSG:5070`).

# In[230]:


s.to_crs('EPSG:5070', inplace=True)
s


# Now we can compute distances to all stadiums in the United States using the [`distance()`](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.distance.html) method.

# In[231]:


distance = stadiums_usa.distance(s['geometry'].iloc[0])
distance 


# Let's add this new data as a column to our original `GeoDataFrame` and convert to kilometers.

# In[232]:


stadiums_usa['distance_to_eugene'] = distance / 1000
stadiums_usa


# Finally, we will plot the data again but this time color the dots based on distance to campus. See [here](https://geopandas.org/en/stable/docs/user_guide/interactive_mapping.html) for more examples of interactive plotting and [here](https://matplotlib.org/stable/tutorials/colors/colormaps.html) for a full list of colormaps.

# In[233]:


stadiums_usa.explore(column='distance_to_eugene', cmap='Set1')


# ```{note}
# The `explore()` method returns a `folium.Map` object which is a really nice way of making interactive maps. We don't have enough time to cover `Folium` in this course. But we use it a lot in **Geospatial Data Science**, the next course in this series. 
# ```

# In[ ]:




