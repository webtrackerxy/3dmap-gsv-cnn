import os,pymap3d,simplekml
import cv2,copy,random,json,math
import Equirec2Perspec as E2P 
from time import sleep
import csv
import base64,zlib
import numpy as np
import struct
import matplotlib.pyplot as plt
import geopy
from geopy.distance import VincentyDistance
import pandas as pd, numpy as np, matplotlib.pyplot as plt, time
from sklearn.cluster import DBSCAN
from sklearn import metrics
from geopy.distance import great_circle
from shapely.geometry import MultiPoint


www_path ="/var/www/html/cesium/download"
base_path = "../../download/download"
base_path_json = "../../download/download"
color_array = ['red','green','yellow','blue','brown','grey', 'black']
shape_array = ['circle','square','diamond','cross','triangle','plus','star','dot']
kml_tree_icon_array = ['tree1_black','tree1_green','tree1_yellow','tree1_red','tree1_blue','tree1_purple']
kml_tree_icon_color_array = ['black','green','yellow','red','blue','purple']

pano_image_height = 1664
pano_image_width  = 3328

kml_single_color_mode = False
kml_show_camera_point = True

trees_latlon_content = []

camera_tree_array = []

tree_depth_array = []

camera_count = 0;

offset_x = 600 # in pixel

cluster_distance = 4 #in meters

road_array = []
#road_array.append("VICTORIA ROAD") #
#road_array.append("HOSPITAL ROAD")
#road_array.append("LOCKHART ROAD")
road_array.append("JOHNSTON ROAD")
#road_array.append("KENNEDY ROAD")
#road_array.append("MAN CHEUNG STREET")

#road_array.append("GLOUCESTER ROAD") #
#road_array.append("HENNESSY ROAD") # -- problem
#road_array.append("MAN CHEUNG STREET")
#road_array.append("LOCKHART ROAD")
#road_array.append("JOHNSTON ROAD")
#road_array.append("LUNG WO ROAD")
#road_array.append("UPPER ALBERT ROAD") #
#road_array.append("LOWER ALBERT ROAD") #
#road_array.append("GARDEN ROAD") #
#road_array.append("KENNEDY ROAD") #
#road_array.append("MACDONNELL ROAD") #
#road_array.append("HORNSEY ROAD") #
#road_array.append("ROBINSON ROAD") #
#road_array.append("CONDUIT ROAD") #
#road_array.append("LYTTELTON ROAD") #
#road_array.append("LEE NAM ROAD") #
#road_array.append("SHEK PAI WAN ROAD") # --problem
#road_array.append("CYBERPORT ROAD") #
#road_array.append("VICTORIA ROAD") #

#road_array.append("POK FU LAM ROAD") #
#road_array.append("SHING SAI ROAD") #
#road_array.append("BONHAM ROAD") #
#road_array.append("HOSPITAL ROAD")
#road_array.append("PO SHAN ROAD") # --
#road_array.append("STUBBS ROAD") #--
#road_array.append("MOUNT BUTLER DRIVE")	

#-------------

def parse(b64_string):
    # fix the 'inccorrect padding' error. The length of the string needs to be divisible by 4.
    b64_string += "=" * ((4 - len(b64_string) % 4) % 4)
    # convert the URL safe format to regular format.
    data = b64_string.replace("-", "+").replace("_", "/")

    data = base64.b64decode(data)  # decode the string
    data = zlib.decompress(data)  # decompress the data
    return np.array([d for d in data])


def parseHeader(depthMap):
    return {
        "headerSize": depthMap[0],
        "numberOfPlanes": getUInt16(depthMap, 1),
        "width": getUInt16(depthMap, 3),
        "height": getUInt16(depthMap, 5),
        "offset": getUInt16(depthMap, 7),
    }


def get_bin(a):
    ba = bin(a)[2:]
    return "0" * (8 - len(ba)) + ba


def getUInt16(arr, ind):
    a = arr[ind]
    b = arr[ind + 1]
    return int(get_bin(b) + get_bin(a), 2)


def getFloat32(arr, ind):
    return bin_to_float("".join(get_bin(i) for i in arr[ind : ind + 4][::-1]))


def bin_to_float(binary):
    return struct.unpack("!f", struct.pack("!I", int(binary, 2)))[0]


def parsePlanes(header, depthMap):
    indices = []
    planes = []
    n = [0, 0, 0]

    for i in range(header["width"] * header["height"]):
        indices.append(depthMap[header["offset"] + i])

    for i in range(header["numberOfPlanes"]):
        byteOffset = header["offset"] + header["width"] * header["height"] + i * 4 * 4
        n = [0, 0, 0]
        n[0] = getFloat32(depthMap, byteOffset)
        n[1] = getFloat32(depthMap, byteOffset + 4)
        n[2] = getFloat32(depthMap, byteOffset + 8)
        d = getFloat32(depthMap, byteOffset + 12)
        planes.append({"n": n, "d": d})

    return {"planes": planes, "indices": indices}


def computeDepthMap(header, indices, planes):

    v = [0, 0, 0]
    w = header["width"]
    h = header["height"]

    depthMap = np.empty(w * h)

    sin_theta = np.empty(h)
    cos_theta = np.empty(h)
    sin_phi = np.empty(w)
    cos_phi = np.empty(w)

    for y in range(h):
        theta = (h - y - 0.5) / h * np.pi
        sin_theta[y] = np.sin(theta)
        cos_theta[y] = np.cos(theta)

    for x in range(w):
        phi = (w - x - 0.5) / w * 2 * np.pi + np.pi / 2
        sin_phi[x] = np.sin(phi)
        cos_phi[x] = np.cos(phi)

    for y in range(h):
        for x in range(w):
            planeIdx = indices[y * w + x]

            v[0] = sin_theta[y] * cos_phi[x]
            v[1] = sin_theta[y] * sin_phi[x]
            v[2] = cos_theta[y]

            if planeIdx > 0:
                plane = planes[planeIdx]
                t = np.abs(
                    plane["d"]
                    / (
                        v[0] * plane["n"][0]
                        + v[1] * plane["n"][1]
                        + v[2] * plane["n"][2]
                    )
                )
                depthMap[y * w + (w - x - 1)] = t
            else:
                depthMap[y * w + (w - x - 1)] = 9999999999999999999.0

            #print(y * w + (w - x - 1))    
    return {"width": w, "height": h, "depthMap": depthMap}


def computeDepthMapDistance(depthMap,x, y):

    w = depthMap["width"]
    pixelIndex = y*w + x
    distance = depthMap["depthMap"][pixelIndex]
    return distance

def computeDepthMapLatLon(s, lat0,lon0, x,y,  heading_angle):

    y  = y + 10

    # decode string + decompress zip
    depthMapData = parse(s)
    # parse first bytes to describe data
    header = parseHeader(depthMapData)
    # parse bytes into planes of float values
    data = parsePlanes(header, depthMapData)
    # compute position and values of pixels
    depthMap = computeDepthMap(header, data["indices"], data["planes"])

    h = depthMap["height"]
    w = depthMap["width"]
    d = computeDepthMapDistance(depthMap,x,y)

    # remap the image center is zero. from left to right ( 0 - 360)
    if x <= depthMap["width"]/2:
    	x0 = (depthMap["width"]/2 - x)
    else:
    	x0 = depthMap["width"] - (x - depthMap["width"]/2) 

    theta = 360/depthMap["width"]*x0 
    theta = (heading_angle+theta)

    origin = geopy.Point(lat0, lon0)
    destination = VincentyDistance(meters=d).destination(origin, theta)
    lat2, lon2 = destination.latitude, destination.longitude

    x0 = int(x/512*pano_image_width)
    y0 = int(y/256*pano_image_height)

    message =  pano_id +"," + str(x) + "," + str(y) + "," + str(x0) + "," + str(y0) + ","+ str(d) + "," +  str(heading_angle) +  "," + str(theta) +"," + str(heading_angle+theta) \
    + "," + 	str(lat2) + "," + str(lon2)				
    #print(d, x, heading_angle, theta, (heading_angle+theta))
    tree_depth_array.append(message)

    return (lat2, lon2, d, theta, depthMap)

def addText(image,text, x,y):
	# font 
	font = cv2.FONT_HERSHEY_SIMPLEX 
	  
	# fontScale 
	fontScale = 0.5
	   
	# Blue color in BGR 
	color = (255, 255, 0) 
	  
	# Line thickness of 2 px 
	thickness = 1

	return cv2.putText(image, str(text), (x+7,y), font, fontScale, color, thickness, cv2.LINE_AA) 

def saveCompositeImage(filename, depthMap, detected_points):
	i =0

	if len(detected_points) <= 0:
		return


	im2 = cv2.imread(base_path_json + "/"+ folder + "/preview/"+filename.rsplit('.', 1)[0]+'.jpg', cv2.IMREAD_COLOR)
	resized = cv2.resize(im2, (depthMap["width"], depthMap["height"]), interpolation = cv2.INTER_AREA)
	clone_img1 = cv2.flip(resized, 1)
	  
	# process float 1D array into int 2D array with 255 values
	im = depthMap["depthMap"]

	#print(len(im))
	im[np.where(im == max(im))[0]] = 255
	if min(im) < 0:
	    im[np.where(im < 0)[0]] = 0
	im = im.reshape((depthMap["height"], depthMap["width"])).astype(int)
	  
	depthma_path_file = 'depthma_path_file.jpg'
	cv2.imwrite( depthma_path_file, im )   

	if os.path.isfile(depthma_path_file):
	    clone_img = cv2.imread(depthma_path_file, cv2.IMREAD_COLOR)     

	for point in detected_points:		
		i = i +1 	
		x = point[0]
		y = point[1]
		cv2.circle(clone_img,(x, y), 5, (255, 0, 255),-1)    
		clone_img2 = addText(clone_img1, i, x,y)


	plt.imshow(clone_img2,cmap='gray') 
	plt.imshow(clone_img,cmap='jet', alpha=0.4)

	plt.savefig(base_path_json + "/"+ folder + "/depthmap/"+filename.rsplit('.', 1)[0]+'.png')

def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)


def calculate_cluster(folder,sep_distance,offset):

	# define the number of kilometers in one radian
	kms_per_radian = 6371.0088

	#folder = "HOSPITAL ROAD"
	#folder = "JOHNSTON ROAD"
	#sep_distance = 4 # in meter
	#offset = 400

	# load the data set(
	df = pd.read_csv('./results/'+folder+'_'+str(offset)+'.csv', sep=',')
	#df = pd.read_csv('2014-summer-travels/data/summer-travel-gps-full.csv', encoding='utf-8')
	#df = pd.read_csv('summer-travel-gps-full.csv', encoding='utf-8')

	df.head()

	# represent points consistently as (lat, lon)
	coords = df.as_matrix(columns=['lat', 'lon'])

	#print(coords)

	# define epsilon as 1.5 kilometers, converted to radians for use by haversine
	#epsilon = 1.5 / kms_per_radian

	# define epsilon as 5 meters, converted to radians for use by haversine
	epsilon = sep_distance/1000/ kms_per_radian

	start_time = time.time()
	db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
	cluster_labels = db.labels_

	#print(cluster_labels)

	# get the number of clusters
	num_clusters = len(set(cluster_labels))

	#print(num_clusters)

	# all done, print the outcome
	message = 'Clustered {:,} points down to {:,} clusters, for {:.1f}% compression in {:,.2f} seconds'

	print(message.format(len(df), num_clusters, 100*(1 - float(num_clusters) / len(df)), time.time()-start_time))
	print('Silhouette coefficient: {:0.03f}'.format(metrics.silhouette_score(coords, cluster_labels)))

	# turn the clusters in to a pandas series, where each element is a cluster of points
	clusters = pd.Series([coords[cluster_labels==n] for n in range(num_clusters)])

	centermost_points = clusters.map(get_centermost_point)

	#print(centermost_points)

	# unzip the list of centermost points (lat, lon) tuples into separate lat and lon lists
	lats, lons = zip(*centermost_points)

	# from these lats/lons create a new df of one representative point for each cluster
	rep_points = pd.DataFrame({'lon':lons, 'lat':lats})
	rep_points.tail()


	# pull row from original data set where lat/lon match the lat/lon of each row of representative points
	# that way we get the full details like city, country, and date from the original dataframe
	rs = rep_points.apply(lambda row: df[(df['lat']==row['lat']) & (df['lon']==row['lon'])].iloc[0], axis=1)
	rs.to_csv('results/'+folder+'_dbscan_'+str(offset)+'_'+str(sep_distance)+'m.csv', encoding='utf-8')
	rs.tail()

def make_kml(folder,csv_file):
	with open(csv_file) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				print("First Row")
				print(row)
			else:
				#print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
				print(row)
				pnt = kml.newpoint(name="", coords=[(row[1],row[0])])
				# https://www.uvic.ca/socialsciences/ethnographicmapping/resources/indigenous-mapping-icons/index.php
				# http://kml4earth.appspot.com/icons.html
				#kml_icon_shape_index= random.randint(0,5)			
				pnt.style.iconstyle.icon.href = '/cesium/assets/tree1_green.png'		
				#pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/parks.png'
				picpath = 'http://localhost:8000/'+folder+'/preview/'+row[7] +'.jpg'
				pnt.description = each_road+ '<br><a href="url">'+ str(row[6]) +'m</a><br>\
				<a href="'+picpath+'" target="_blank"><img src="' + picpath +'" alt="picture" width="400" height="200" align="left" /></a>'

			line_count += 1


	"""
	with open(csv_file) as csv_file:
	    csv_reader = csv.reader(csv_file, delimiter=',')
	    line_count = 0
	    for row in csv_reader:
	        if line_count == 0:
	            print(f'Column names are {", ".join(row)}')
	            line_count += 1
	        else:
	            print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
	            line_count += 1

	    print(f'Processed {line_count} lines.')
	"""
#-------------


if __name__ == '__main__':


	for each_road in road_array:

		kml=simplekml.Kml()
		pano_trees = dict()
		count = 0

		print("----  " + each_road + " --------")

		base_dir = base_path + "/" + each_road
		preview_dir = base_path + "/" + each_road +"/preview"
		detected_trees_file = base_dir + "/" + "perspective/processed/trees_detected.txt"


		if not os.path.exists(preview_dir):
			os.makedirs(preview_dir)
		
		with open(detected_trees_file, "r") as ins:
			detected_trees = []		
			for line in ins:
				detected_trees.append(line)
				

		file = open("./results/"+each_road + "_pano_trees.txt","w+")

		for detected_tree in detected_trees:

			record = detected_tree.split(",")
			fname = record[1][0:22]
			
			empty, fov, theta, phi = record[1][22:].split(".")[0].split("_")
			detected_x = int(record[7])
			detected_y = int(record[8])		
			
			phi_offset = 0 # shift the PI angle
			#print(base_dir + "/" +fname +".jpg")
			equ = E2P.Equirectangular(base_dir + "/" +fname +".jpg")    # Load equirectangular image
			result = equ.CheckPerspective(114,int(theta) , int(phi)-phi_offset, 418, 418, detected_x, detected_y) # Specify parameters(FOV, theta, phi, height, width)
			
			detected_pano_x  = int(result[2])
			detected_pano_y	 = int(result[3])
			detected_pano_depth_x	 = int(result[4])
			detected_pano_depth_y	 = int(result[5])						
			#print(result)			
			try:
				pano_trees[fname].append((detected_pano_x,detected_pano_y,detected_pano_depth_x,detected_pano_depth_y))				
			except:
				pano_trees[fname] = []			
				pano_trees[fname].append((detected_pano_x,detected_pano_y,detected_pano_depth_x,detected_pano_depth_y))				
  							
			print( each_road +","+ fname + ''.join(","+str(e) for e in result))			
			file.write('\n'+ each_road +","+ fname + ''.join(","+str(e) for e in result))
			

			#for xy in pano_trees[fname]:
			#	for xy2 in pano_trees[fname]:
			#		if (xy[0] != xy2[0] and xy[0] != xy2[0]) and (abs(xy[0]-xy2[0]) <= 100): # 30 pixels difference
			#			pano_trees[fname].remove(xy2)


		#print(pano_trees)
		file.close
		# create a detected point in the pano image
		"""
		for fname in pano_trees:
			for points in pano_trees[fname]:
				
				original_file = base_dir+"/"+fname +".jpg" 
				process_file = preview_dir+"/"+fname +".jpg"			
				if os.path.isfile(process_file):
					clone_img = cv2.imread(process_file, cv2.IMREAD_COLOR)
				else:
					clone_img = cv2.imread(original_file, cv2.IMREAD_COLOR)	
					#clone_img = copy.copy(equ._img)		

				cv2.circle(clone_img,(points[0], points[1]), 15, (0, 255, 0),-1)	
				cv2.imwrite( process_file, clone_img )
				#print(".")	
		"""
		""" Processing tree lat,lon"""
		pano_images =  dict()
		pano_data = []

		folder = each_road 

		#print("----" + folder + "-------")
		for filename in os.listdir(base_path + "/"+ folder):

			if filename.endswith(".jpg"):

				count = count + 1

				if os.path.isfile(base_path_json + "/"+ folder + "/"+filename.rsplit('.', 1)[0] + ".json"):

					json_txt = open(base_path_json + "/"+ folder + "/"+filename.rsplit('.', 1)[0]+'.json', 'r').read()

					try:
						loaded_json = json.loads(json_txt)
					except:
						print("error in json:" + filename.rsplit('.', 1)[0]+".json")

					#print(loaded_json)
					
					pano_data = []
					try:
						pano_data.append(float(loaded_json['Projection']['pano_yaw_deg'])) # Center Heading
						pano_data.append(loaded_json['Location']['panoId'])
						pano_data.append(float(loaded_json['Location']['lat'])) 
						pano_data.append(float(loaded_json['Location']['lng'])) 
						pano_data.append(loaded_json['model']['depth_map'])
						#print(loaded_json['model']['depth_map'])
						#print(pano_data)
						#break
					except:
						continue						 																						
					"""
					for item in loaded_json:
						#sleep(0.01)
						if item =="Data":
							'''
							"image_width":"13312",
							"image_height":"6656",
							"tile_width":"512",
							"tile_height":"512",
							"image_date":"2017-01",
							"imagery_type":1,
							"copyright":" 2019 Google"
							'''
							#item_json = loaded_json[item]
							#for sub_item in item_json:
							#	print(sub_item,item_json[sub_item])
							#print(item_json['image_width'])
							#print(item_json['image_height'])
							#print(item_json['tile_width'])
							#print(item_json['tile_height'])
							#print(item_json['image_date'])
							#pano_data.append(item_json['image_date'])
							#print(item_json['imagery_type'])
						elif item =="Projection":
							'''
							"projection_type":"spherical",
							"pano_yaw_deg":"76.74",
							"tilt_yaw_deg":"-112.79",
							"tilt_pitch_deg":"3.04"
							'''
							item_json = loaded_json[item]
							#print(item_json['pano_yaw_deg'])
							#print(item_json['tilt_yaw_deg'])
							#print(item_json['tilt_pitch_deg'])
							pano_data.append(float(item_json['pano_yaw_deg'])) # Center Heading
							#pano_data.append(float(item_json['tilt_yaw_deg']))
							#pano_data.append(float(item_json['tilt_pitch_deg']))	

						elif item =="Location":
							'''
							"panoId":"tIYkK-jdhLpKIH34IRCYrQ",
							"zoomLevels":"5",
							"lat":"22.411916",
							"lng":"114.107863",
							"original_lat":"22.411977",
							"original_lng":"114.107817",
							"elevation_wgs84_m":"433.206572",
							"description":"Rte Twisk",
							"region":"Hong Kong, New Territories",
							"country":"Hong Kong",
							"best_view_direction_deg":"33.0156",
							"elevation_egm96_m":"435.768616"
							'''	
							item_json = loaded_json[item]
							panoId = item_json['panoId']
							#print(item_json['panoId'])
							#print(item_json['zoomLevels'])
							#print(item_json['lat'])	
							#print(item_json['lng'])		
							#print(item_json['original_lat'])		
							#print(item_json['original_lng'])		
							#print(item_json['elevation_wgs84_m'])		
							#print(item_json['best_view_direction_deg'])		
							#print(item_json['elevation_egm96_m'])		

							#pano_data.append(item_json['panoId'])
							#pano_data.append(int(item_json['zoomLevels']))
							pano_data.append(panoId)
							#pano_data.append(float(item_json['lat']))
							#pano_data.append(float(item_json['lng']))		
							pano_data.append(float(item_json['original_lat']))
							pano_data.append(float(item_json['original_lng']))						
							#pano_data.append(float(item_json['best_view_direction_deg']))		


						elif item =="model":	
							'''
							"depth_map":
							'''
							item_json = loaded_json[item]
							#print(item_json['depth_map'])
							#pano_data.append(item_json['depth_map'])		
					"""
					pano_data.append(folder)	
					
				pano_images[filename.rsplit('.', 1)[0]] = pano_data	
				#print(pano_data)
	   			
		
		#print(pano_trees)			
		for pano_id in pano_trees:	

			try:
				i=0	
				j=0
				delected_points = []

				color_index= random.randint(0,6)
				shape_index= random.randint(0,7)
				yaw = pano_images[pano_id][0]	
				#print(pano_images[pano_id][4])	
				#break
				theta=float(yaw)
				if yaw < 180 : #?
					#try:
					message = str(pano_images[pano_id][2])+"	" + str(pano_images[pano_id][3]) + "	"+ str(shape_array[shape_index]) + "5	" +  str(color_array[color_index]) + "	" +  str(0) +"	" + "("+str(yaw) +")-" + pano_id+ "	" +"C"+ "	" +pano_id
					#trees_latlon_content.append(message)
					#print(message)
					
					if kml_single_color_mode:
						kml_tree_icon_color = 3 #red
					else:	
						kml_tree_icon_color = random.randint(0,5)

					if (kml_show_camera_point):
						pnt = kml.newpoint(name="", coords=[(pano_images[pano_id][3],pano_images[pano_id][2])])
						pnt.style.labelstyle.color = simplekml.Color.red  # Make the text red
						pnt.style.labelstyle.scale = 1  # Make the text twice as big
						pnt.style.iconstyle.icon.href = '/cesium/assets/placemark_circle_'+kml_tree_icon_color_array[kml_tree_icon_color]+'.png';
						picpath = 'http://localhost:8000/'+folder+'/preview/'+pano_id +'.jpg'
						#http://localhost:8000/BONHAM%20ROAD/preview/-DldWl1bJF3rdEVUY_Q_Qg.jpg
						pnt.description = each_road+ '<br><a href="url">'+str(0) +"	" + "("+str(yaw) +")-" + pano_id +'</a><br>\
						<a href="'+picpath+'" target="_blank"><img src="' + picpath +'" alt="picture" width="400" height="200" align="left" /></a>'
							
					for pos in range(len(pano_trees[pano_id])):	

						x0 = pano_trees[pano_id][i][0]		
						y0 = pano_trees[pano_id][i][1]

						x = pano_trees[pano_id][i][2]		
						y = pano_trees[pano_id][i][3]

						#print("==>", x,y)
						lat0 = pano_images[pano_id][2]
						lon0 = pano_images[pano_id][3]
						(lat,lon, distance, angle, depthMap) = computeDepthMapLatLon(pano_images[pano_id][4],lat0,lon0,x,y,yaw)

						# process float 1D array into int 2D array with 255 values
						"""
						im = depthMap["depthMap"]
						#print(len(im))
						im[np.where(im == max(im))[0]] = 255
						if min(im) < 0:
						    im[np.where(im < 0)[0]] = 0
						im = im.reshape((depthMap["height"], depthMap["width"])).astype(int)

						if not os.path.exists(base_path + "/" + folder+'/depthmap'):
							os.makedirs(base_path + "/" + folder+'/depthmap')

						depthma_path_file = base_path + "/" + folder+'/depthmap/'+pano_id +'.jpg'
						cv2.imwrite( depthma_path_file, im )   

						
						if os.path.isfile(depthma_path_file):
							clone_img = cv2.imread(depthma_path_file, cv2.IMREAD_COLOR)		
						#clone_img1 = cv2.flip(clone_img, 1)	# ??
						cv2.circle(clone_img,(x, y), 5, (0, 255, 0),-1)		
						cv2.imwrite( depthma_path_file, clone_img )
						"""
						if distance > 1000:
							
							#yyyy=0
							print("Error:",lat,lon,distance,angle)

						else:

							x_offset_left_1 = offset_x  
							x_offset_left_2 = 3328/2 - x_offset_left_1
							x_offset_right_1 = 3328/2 + x_offset_left_1						
							x_offset_right_2 = 3328 - x_offset_left_1


							if distance < 30.0:
								camera_tree = str(lat0) +"," + str(lon0)+ "," + str(round(angle,2))+"," + str(round(distance+2,1))+"," + pano_id+"," + str(camera_count) +","+str(lat)+","+str(lon)
								camera_tree_array.append(camera_tree)

							if distance < 20.0 and ((x0 >= x_offset_left_1 and x0<=x_offset_left_2) or (x0 >= x_offset_right_1 and x0<=x_offset_right_2)):# only show tree within 20m
								j=j+1
								trees_latlon = str(lat)+"," + str(lon) + "," +  str(int(x)) + "," + str(int(y)) + "," + str(count) +","  + str(j) +","  +str(distance) + "," +pano_id
								print(trees_latlon)
								trees_latlon_content.append(trees_latlon)

								delected_points.append((x,y))

						i = i + 1	

					camera_count = camera_count + 1	
					#print(delected_points)


					if not os.path.exists(base_path + "/" + folder+'/depthmap'):
						os.makedirs(base_path + "/" + folder+'/depthmap')	
									
					saveCompositeImage(pano_id, depthMap, delected_points )
			except:
				 print("An exception occurred: panoid:" + pano_id)		


		# --------------- save files ---------------
		file = open("./results/"+each_road + "_"+str(offset_x)+".csv","w+")
		content = 'lat,lon,x,y,num,seq,distance,panoid\n'
		content = content + '\n'.join(trees_latlon_content)
		file.write(content)
		file.close
		

		#print(camera_tree_array)
		file = open("./results/"+each_road + "_camera_points.csv","w+")
		file.write('\n'.join(camera_tree_array))
		file.close

		#print(pano_trees)
		#file = open("./results/"+each_road + "_pano_trees.txt","w+")
		#file.write('\n'.join(pano_trees))
		#file.close
		#for p in pano_trees:
		#	print(p)

		"""
		camera_tree_array2 = []

		#  ROAD sequence
		
		pano_points_array = [line.rstrip('\n') for line in open("./results/"+each_road + "_sorted_panoid.txt")]
		print(pano_points_array)
		print(camera_tree_array)
		for p in pano_points_array:
			print(p)		
			for c in camera_tree_array:
				cc = c.split(",")
				#print(cc[5],p)
				if cc[4] == p:
					#print(cc[4],p,c)
					camera_tree_array2.append(c)

			#break		

		file = open("./results/"+each_road + "_sorted_camera_points.csv","w+")
		file.write('\n'.join(camera_tree_array2))
		file.close
		"""

		#print(tree_depth_array)
		file = open("./results/"+each_road + "_depth_tree_points.csv","w+")
		file.write('\n'.join(tree_depth_array))
		file.close		


		calculate_cluster(each_road,cluster_distance,offset_x)

		if  not os.path.exists(www_path + "/" + folder):
			os.mkdir(www_path + "/" + folder)	

		make_kml(each_road,"./results/"+folder + "_"+str(offset_x)+".csv")
		kml_file = www_path + "/" + folder + "/results.kml"	
		kml.save(kml_file)	