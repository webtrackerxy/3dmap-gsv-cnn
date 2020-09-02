import os
for folder in os.listdir("./download"):
	
	folder = os.path.join("download/", folder)
	crop_folder = os.path.join(folder, "cropped")	
	print(folder, crop_folder)
	if not os.path.isdir(crop_folder):
		os.mkdir(crop_folder)
	for filename in os.listdir(folder):
		if filename.endswith(".jpg"):
			file=os.path.join(folder, filename)
			crop_file = os.path.join(crop_folder+"/" , filename)
			#print(file, crop_file)
			if not os.path.exists(crop_file):
				command = 'convert "' + file+'" -crop 416x208+0+0 "'+ crop_file + '"'
				print(command)
				os.system(command)			
