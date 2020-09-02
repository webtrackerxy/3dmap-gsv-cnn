#114.107885561442 22.4119481300164
#{'lat': 22.41211986716254, 'panoid': u'mcvgKOhrBkS-r6LVBy0kEg', 'lon': 114.1086432178877}
'''
export PATH=$PATH:/Applications/Postgres.app/Contents/Versions/9.3/bin/
pip3 install psycopg2

PostgreSQL Python
http://tw.gitbook.net/postgresql/2013080998.html
'''
import sys, os , shutil
import json,urllib2
import psycopg2
import time

base_path = "./download/"
sleep_time = 1.5 # 2 seconds
reset_tables = False
process_data_download = True 
process_image_download = True
save_image_db = False

# clean the temp folder
folder = './download/tmp/'

cmd = 'rm ' + folder  + '*'
print(cmd)
os.system(cmd)

# 
road_array = []
#road_array.append("GLOUCESTER ROAD") #
#road_array.append("HENNESSY ROAD") #
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
#road_array.append("SHEK PAI WAN ROAD") # --
#road_array.append("CYBERPORT ROAD") #
#road_array.append("VICTORIA ROAD") #
#road_array.append("POK FU LAM ROAD") #
#road_array.append("SHING SAI ROAD") #
#road_array.append("BONHAM ROAD") #
#road_array.append("HOSPITAL ROAD")
#road_array.append("PO SHAN ROAD") # --
#road_array.append("STUBBS ROAD") #--
#road_array.append("MOUNT BUTLER DRIVE")


conn = psycopg2.connect(database="projFYP", user="postgres", password="postgres", host="127.0.0.1", port="5432")
print("Opened database successfully")
cur = conn.cursor()
cur2 = conn.cursor()


if reset_tables:
	sql = "ALTER SEQUENCE pano_sequence RESTART WITH 1"
	cur.execute(sql)
	sql = "DROP TABLE pano_data"
	cur.execute(sql)	
	sql = "\
	CREATE TABLE pano_data\
	(\
	  objectid bigint NOT NULL,\
	  image_date date,\
	  pano_yaw_deg numeric,\
	  tilt_yaw_deg numeric,\
	  tilt_pitch_deg numeric,\
	  panoid character varying(255),\
	  zoomlevels integer,\
	  lat numeric,\
	  lng numeric,\
	  best_view_direction_deg numeric,\
	  depth_map text,\
	  geom geometry,\
	  CONSTRAINT pano_primary_key PRIMARY KEY (objectid)\
	)\
	WITH (\
	  OIDS=FALSE\
	);"
	cur.execute(sql)

	#-- Table: pano_data_direction	
	sql = "ALTER SEQUENCE pano_direction_sequence RESTART WITH 1"
	cur.execute(sql)
	sql = "DROP TABLE pano_data_direction"
	cur.execute(sql)
	sql = "\
		CREATE TABLE pano_data_direction\
		(\
		  objectid bigint NOT NULL,\
		  panoId character varying(255),\
		  yawDeg numeric,\
		  targetpanoid character varying(255),\
		  road_argb character varying(255),\
		  description character varying(255),\
		  CONSTRAINT pano_direction_primary_key PRIMARY KEY (objectid)\
		)\
		WITH (\
		  OIDS=FALSE\
		);\
		ALTER TABLE pano_data_direction\
		  OWNER TO postgres;"
	cur.execute(sql)	  


	conn.commit()   

# select road from database

for each_road in road_array:

	if  not os.path.exists(base_path+each_road):
		os.mkdir(base_path+each_road)

	#sql = "SELECT l.street_ena, ST_X(p.geom), ST_Y(p.geom) FROM centreline_hongkongisland l, road_points_hongkongisland p WHERE l.objectid = p.road_objectid \
	#and l.street_ena='"+each_road+"' LIMIT 40"
	sql = "SELECT l.street_ena, ST_X(p.geom), ST_Y(p.geom) FROM centreline_hongkongisland l, road_points_hongkongisland p WHERE l.objectid = p.road_objectid \
	and l.street_ena='"+each_road+"'"
	print(sql)

	try:
		cur.execute(sql)
	except:
	    print "I can't SELECT road"

	rows = cur.fetchall()
	print "\nRows: \n"
	point = {}
	#pano_point_array = []
	for row in rows:

		time.sleep(sleep_time)

		print row[0] , row[1] , row[2]
		point['lng'] = row[1]
		point['lat'] = row[2]
		#pano_point_array.append(point)


		'''
		sql = "SELECT street_ena, ST_AsText(geom) FROM centreline_hongkongisland WHERE street_ena='MAN CHEUNG STREET'"
		print(sql)
		try:
			cur.execute(sql)
		except:
		    print "I can't SELECT"

		rows = cur.fetchall()
		print "\nRows: \n"
		for row in rows:
			print "   ", row[0] , row[1] 
			sql2 = "SELECT ST_X(d.geom), ST_Y(d.geom)\
			FROM ST_DumpPoints('"+ row[1] + "') AS d;"
			#print(sql2)
			cur2.execute(sql2)
			rows2 = cur2.fetchall()
			for row2 in rows2:	
				print "   ", row2[0] , row2[1]  
		'''


		#https://deviceatlas.com/blog/list-of-user-agent-strings
		headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246' }
		#headers = { 'User-Agent' : 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36' }
		#headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9' }
		#url = 'http://maps.google.com/cbk?output=json&ll=22.4119481300164,114.107885561442&dm=1'
		url = 'http://maps.google.com/cbk?output=json&ll='+str(point['lat'])+','+str(point['lng'])+'&dm=1'
		req = urllib2.Request(url, None, headers)
		html = urllib2.urlopen(req).read()


		loaded_json = json.loads(html)

		pano_data = []
		for item in loaded_json:

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
				item_json = loaded_json[item]
				#for sub_item in item_json:
				#	print(sub_item,item_json[sub_item])
				#print(item_json['image_width'])
				#print(item_json['image_height'])
				#print(item_json['tile_width'])
				#print(item_json['tile_height'])
				#print(item_json['image_date'])
				pano_data.append(item_json['image_date'])
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
				pano_data.append(float(item_json['pano_yaw_deg']))
				pano_data.append(float(item_json['tilt_yaw_deg']))
				pano_data.append(float(item_json['tilt_pitch_deg']))	
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

				pano_data.append(item_json['panoId'])
				pano_data.append(int(item_json['zoomLevels']))
				pano_data.append(float(item_json['lat']))
				pano_data.append(float(item_json['lng']))		
				pano_data.append(float(item_json['best_view_direction_deg']))		

			elif item =="Links":
				'''
				{
				"yawDeg":"253.94",
				"panoId":"0QNhaaiqtDGmkwE7CZupkA",
				"road_argb":"0x80fdf872",
				"description":"Rte Twisk"
				},
				{
				"yawDeg":"78.8",
				"panoId":"44LEGX6vk2nAxOHQEtoRGg",
				"road_argb":"0x80fdf872",
				"description":"Rte Twisk"
				}
				'''		
				item_json_direction = loaded_json[item]
				#print(item_json_direction)
				ii=0

				for direction_items in item_json_direction:
					pano_data_direction = []				
					ii = ii + 1
					print ii, direction_items
					pano_data_direction.append(loaded_json['Location']['panoId'])								
					pano_data_direction.append(float(direction_items['yawDeg']))				
					pano_data_direction.append(direction_items['panoId'])
					pano_data_direction.append(direction_items['road_argb'])
					pano_data_direction.append(direction_items['description'])	

					#print(pano_data_direction)
					if save_image_db:
						sql_direction = "INSERT INTO pano_data_direction (objectid, panoId, yawDeg, targetpanoid, road_argb, description  \
						) VALUES(nextval('pano_direction_sequence'), '%s', %f, '%s', '%s', '%s' )" % tuple(pano_data_direction)
						print(sql_direction)
						try:
							cur.execute(sql_direction)
						except:
						    print("INSERT pano_data_direction FAIL")
							
						conn.commit()
			elif item =="model":	
				'''
				"depth_map":
				'''
				item_json = loaded_json[item]
				#print(item_json['depth_map'])
				#pano_data.append(item_json['depth_map'])		



		if process_data_download:

			geom = "ST_MakePoint("+item_json['lng']+","+ item_json['lat']+")";
			pano_data.append(geom)		

			#print(pano_data)

			#save the file
			if not os.path.exists(base_path+each_road):
				print("directory not exist:" + base__path+each_road)
				sys.exit(os.EX_OK)

			f = open(base_path+each_road+"/" + panoId +".json", "w")
			f.write(html)
			f.close()

			#download the pano image
			'''
			if process_image_download:
				opener = urllib2.build_opener()
				opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36')]
				url = 'http://maps.google.com/cbk?output=tile&panoid='+panoId+'&zoom=0&x=0&y=0'
				response = opener.open(url)
				htmlData = response.read()
				f = open(base_path+each_road+'/'+panoId+'.jpg','w')
				f.write(htmlData)
				f.close()
			'''



			#clean tmp folder
			#...

			for x in range(0, 7):
				for y in range(0, 4):
					#print(str(x) + " " + str(y))
					#download the pano image
					opener = urllib2.build_opener()
					opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36')]
					url = 'http://maps.google.com/cbk?output=tile&panoid='+panoId+'&zoom=3&x='+str(x)+'&y='+str(y)
					response = opener.open(url)
					htmlData = response.read()
					f = open(folder+panoId+'_'+str(x)+'_'+str(y)+'_3.jpg','w')
					f.write(htmlData )
					f.close()


			pano_file = panoId + '_.jpg'
			crop_pano_file = panoId + '.jpg'

			cmd_string = ""
			for x in range(0, 4):
				for y in range(0, 7):
					#print(str(x) + " " + str(y))		
					cmd_string = cmd_string + " " + folder + panoId +'_' +str(y)+'_'+str(x)+'_3.jpg'


			cmd = 'montage ' + cmd_string +  ' -mode Concatenate -tile 7x4 ' + folder + pano_file
			print(cmd)
			os.system(cmd)

			cmd = 'convert "' + folder +pano_file +'" -crop 3328x1664+0+0 "'+ base_path+each_road +'/' + crop_pano_file + '"'
			print(cmd)
			os.system(cmd)			

			# insert into database
			if save_image_db:
				sql = "INSERT INTO pano_data (objectid,image_date, pano_yaw_deg, tilt_yaw_deg, tilt_pitch_deg, panoId , \
				zoomLevels, lat, lng, best_view_direction_deg,geom) \
				VALUES(nextval('pano_sequence'),'%s-01', %f, %f, %f, '%s', %i, %f, %f, %f, %s)" % tuple(pano_data)

				print(sql)
				try:
					cur.execute(sql)
				except:
				    print("INSERT pano_data FAIL")


				# insert into database
				'''
				sql = "INSERT INTO pano_data_depth (objectid, panoid, depth_map) \
				VALUES(nextval('pano_sequence'),'%s-01', %f, %f, %f, '%s', %i, %f, %f, %f, %s)" % tuple(pano_data_depth)

				print(sql)
				try:
					cur.execute(sql)
				except:
				    print("INSERT FAIL")
				'''

			
				conn.commit()    


		#sys.exit(os.EX_OK) # code 0, all ok	

conn.close()