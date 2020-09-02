import glob
import os,shutil
dir = "/home/bluesky/project/LSGI552 Project/download/trainning2/1/"
to_dir = "/home/bluesky/project/LSGI552 Project/download/trainning2/2/"

for file in glob.glob(dir+"*.jpg"):
	file2=os.path.basename(file)
	#print(os.path.splitext(file))
	anno_file = os.path.splitext(file2)[0]+ ".txt"
	if  not os.path.isfile(dir + anno_file):
		print(file)
		#shutil.move(file, to_dir)