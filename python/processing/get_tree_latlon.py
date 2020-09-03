import os,pymap3d,simplekml
import cv2,copy,random,json,math
import Equirec2Perspec as E2P 
from time import sleep
import csv
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
kml_show_camera_point = False

trees_latlon_content = []

camera_tree_array = []

camera_count = 0;

offset_x = 700 # in pixel

cluster_distance = 4 #in meters

road_array = []
#road_array.append("VICTORIA ROAD") #
#road_array.append("HOSPITAL ROAD")
road_array.append("JOHNSTON ROAD")
#road_array.append("KENNEDY ROAD")
#road_array.append("MAN CHEUNG STREET")
"""
road_array.append("GLOUCESTER ROAD") #
road_array.append("HENNESSY ROAD") #
road_array.append("MAN CHEUNG STREET")
road_array.append("LOCKHART ROAD")
road_array.append("JOHNSTON ROAD")
road_array.append("LUNG WO ROAD")
road_array.append("UPPER ALBERT ROAD") #
road_array.append("LOWER ALBERT ROAD") #
road_array.append("GARDEN ROAD") #
road_array.append("KENNEDY ROAD") #
road_array.append("MACDONNELL ROAD") #
road_array.append("HORNSEY ROAD") #
road_array.append("ROBINSON ROAD") #
road_array.append("CONDUIT ROAD") #
road_array.append("LYTTELTON ROAD") #
road_array.append("LEE NAM ROAD") #
road_array.append("SHEK PAI WAN ROAD") # --
road_array.append("CYBERPORT ROAD") #
road_array.append("VICTORIA ROAD") #

road_array.append("POK FU LAM ROAD") #
road_array.append("SHING SAI ROAD") #
road_array.append("BONHAM ROAD") #
road_array.append("HOSPITAL ROAD")
road_array.append("PO SHAN ROAD") # --
road_array.append("STUBBS ROAD") #--
road_array.append("MOUNT BUTLER DRIVE")	
	"""



def angle_from_coordinate(p1, p2):

	lat1 = p1[0]
	long1 = p1[1]
	lat2 = p2[0]
	long2 =p2[1]

	dLon = (long2 - long1)

	y = math.sin(dLon) * math.cos(lat2)
	x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)

	brng = math.atan2(y, x)

	brng = math.degrees(brng)
	brng = (brng + 360) % 360
	brng = 360 - brng # count degrees clockwise - remove to make counter-clockwise

	return brng

def cal_distance_latlon(p1,p2):
	# approximate radius of earth in km
	R = 6373.0

	lat1 = math.radians(p1[0])
	lon1 = math.radians(p1[1])
	lat2 = math.radians(p2[0])
	lon2 = math.radians(p2[1])

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

	distance = R * c
	return distance*1000 # in meter


def cal_ex_ey(x,y,yaw,lat0,lon0,count,remarks,color,kml_color,shape):

	h = 2.5
	yaw = float(yaw)
	#c = float(yaw*math.pi/180)
	c = float(yaw*math.pi/180) + math.pi # require to add PI to correct the orientation
	#print(-y*math.pi/pano_image_height + math.pi/2)
	z = -h/math.tan(-y*math.pi/pano_image_height + math.pi/2)
	ex = math.sin(x*2*math.pi/pano_image_width - math.pi + c)*z
	ey = math.cos(x*2*math.pi/pano_image_width - math.pi + c)*z

	#print(x,y,c,z,ex,ey)
	
	u  = z
	e = ex
	n = ey
	h0 = 2.5
	#try:
	r = pymap3d.enu2geodetic(e, n,u, float(lat0), float(lon0), h0)		
	# http://www.copypastemap.com/
	distance = cal_distance_latlon((lat0,lon0),(r[0],r[1]))
	angle = angle_from_coordinate((lat0,lon0),(r[0],r[1]))
	#print(angle)

	return distance, angle, r[0], r[1]
	#except:
	#	print("Error:pymap3d.enu2geodetic")	
	#	print("cal_ex_ey",x,y,yaw,lat0,lon0,count)

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
				

		for detected_tree in detected_trees:

			record = detected_tree.split(",")
			fname = record[1][0:22]
			
			empty, fov, theta, phi = record[1][22:].split(".")[0].split("_")
			detected_x = int(record[7])
			detected_y = int(record[8])		
			
			phi_offset = 0 # shift the PI angle
			equ = E2P.Equirectangular(base_dir + "/" +fname +".jpg")    # Load equirectangular image
			result = equ.CheckPerspective(114,int(theta) , int(phi)-phi_offset, 418, 418, detected_x, detected_y) # Specify parameters(FOV, theta, phi, height, width)
			
			detected_pano_x  = int(result[2])
			detected_pano_y	 = int(result[3])
						
			try:
				pano_trees[fname].append((detected_pano_x,detected_pano_y))				
			except:
				pano_trees[fname] = []			
				pano_trees[fname].append((detected_pano_x,detected_pano_y))				
  							
			print( each_road +","+ fname + ''.join(","+str(e) for e in result))			


			for xy in pano_trees[fname]:
				for xy2 in pano_trees[fname]:
					if (xy[0] != xy2[0] and xy[0] != xy2[0]) and (abs(xy[0]-xy2[0]) <= 100): # 30 pixels difference
						pano_trees[fname].remove(xy2)


		#print(pano_trees)
		
		# create a detected point in the pano image
		
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
			i=0	

			color_index= random.randint(0,6)
			shape_index= random.randint(0,7)
			yaw = pano_images[pano_id][0]		
			theta=float(yaw)
			if yaw < 180: #?
				#try:
				#message = str(pano_images[pano_id][2])+"	" + str(pano_images[pano_id][3]) + "	"+ str(shape_array[shape_index]) + "5	" +  str(color_array[color_index]) + "	" +  str(0) +"	" + "("+str(yaw) +")-" + pano_id+ "	" +"C"+ "	" +pano_id
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
				
				seq_count  =0 		
				for pos in range(len(pano_trees[pano_id])):	

					x = pano_trees[pano_id][i][0]		
					y = pano_trees[pano_id][i][1]

					lat0 = pano_images[pano_id][2]
					lon0 = pano_images[pano_id][3]

					distance, angle, lat, lon =  cal_ex_ey(x,y,theta,lat0,lon0,str(i+1), str(x)+"-"+ str(y)+"-("+str(yaw) +")-"+pano_id,str(color_array[color_index]),str(kml_tree_icon_color_array[kml_tree_icon_color]),str(shape_array[shape_index])+"1")		

					x_offset_left_1 = offset_x  
					x_offset_left_2 = 3328/2 - x_offset_left_1
					x_offset_right_1 = 3328/2 + x_offset_left_1						
					x_offset_right_2 = 3328 - x_offset_left_1

					if distance < 30.0:
						camera_tree = str(lat0) +"," + str(lon0)+ "," +str(round(angle,2))+"," + str(round(distance+2,1))+"," + pano_id+"," + str(camera_count) +","+str(lat)+","+str(lon)
						camera_tree_array.append(camera_tree)

					if distance < 20.0 and ((x >= x_offset_left_1 and x<=x_offset_left_2) or (x >= x_offset_right_1 and x<=x_offset_right_2)):# only show tree within 20m


						seq_count = seq_count + 1

						camera_tree = str(lat0) +"," + str(lon0)+ "," + str(round(angle,2))+"," + str(round(distance+2,1))+"," + pano_id+"," + str(camera_count) +","+str(lat)+","+str(lon)
						camera_tree_array.append(camera_tree)

						trees_latlon = str(lat)+"," + str(lon) + "," + str(x) + "," + str(y) + "," +  str(count) +","   +str(distance) + "," + str(seq_count) +"," + pano_id
						print(trees_latlon)
						trees_latlon_content.append(trees_latlon)


						"""
						pnt = kml.newpoint(name="", coords=[(r[1],r[0])])
						# https://www.uvic.ca/socialsciences/ethnographicmapping/resources/indigenous-mapping-icons/index.php
						# http://kml4earth.appspot.com/icons.html
						#kml_icon_shape_index= random.randint(0,5)			
						pnt.style.iconstyle.icon.href = '/cesium/assets/tree1_' + kml_color+  ".png"		
						#pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/parks.png'
						picpath = 'http://localhost:8000/'+folder+'/preview/'+pano_id +'.jpg'
						pnt.description = each_road+ '<br><a href="url">'+remarks +'=>' +str(distance) +'m</a><br>\
						<a href="'+picpath+'" target="_blank"><img src="' + picpath +'" alt="picture" width="400" height="200" align="left" /></a>'
						"""
						"""
						original_file = base_dir+"/"+pano_id +".jpg" 
						process_file = preview_dir+"/"+pano_id +".jpg"

						#print(original_file,process_file)			
						if os.path.isfile(process_file):
							clone_img = cv2.imread(process_file, cv2.IMREAD_COLOR)
						else:
							clone_img = cv2.imread(original_file, cv2.IMREAD_COLOR)	
						
						cv2.circle(clone_img,(x, y), 30, (0, 255, 0),-1)	
						cv2.imwrite(process_file, clone_img)
						"""						

					i = i + 1			
					#except:
					#	print("Error:", pano_id)
				camera_count = camera_count + 1	

		# --------------- save files ---------------
		#print(trees_latlon_content[5],trees_latlon_content[0],trees_latlon_content[1])
		#print('\n'.join(trees_latlon_content))	
		#file = open("./results/"+each_road + ".txt","w+")
		#file = open("./results/"+each_road + ".csv","w+")
		#file.write('\n'.join(trees_latlon_content))
		#file.close
		
		file = open("./results/"+each_road + "_"+str(offset_x)+".csv","w+")
		content = 'lat,lon,x,y,num,seq,distance,panoid\n'
		content = content + '\n'.join(trees_latlon_content)
		file.write(content)
		file.close	

		#print(camera_tree_array)
		file = open("./results/"+each_road + "_camera_points.csv","w+")
		file.write('\n'.join(camera_tree_array))
		file.close

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


		calculate_cluster(each_road,cluster_distance,offset_x)

		if  not os.path.exists(www_path + "/" + folder):
			os.mkdir(www_path + "/" + folder)	

		make_kml(each_road,"./results/"+folder + "_"+str(offset_x)+".csv")
		kml_file = www_path + "/" + folder + "/results.kml"	
		kml.save(kml_file)	