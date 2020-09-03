import os,glob
import cv2 
import Equirec2Perspec as E2P 

def makeEquirectangular(fullpath,perspective_path):
    equ = E2P.Equirectangular(fullpath)    # Load equirectangular image    
    #
    # FOV unit is degree 
    # theta is z-axis angle(right direction is positive, left direction is negative)
    # phi is y-axis angle(up direction positive, down direction negative)
    # height and width is output image dimension 
    #
    #image_array = equ.GetPerspective(60, 0, 0, 720, 1080) # Specify parameters(FOV, theta, phi, height, width)
    #cv2.imwrite( "src/RYnPzd7B05KReFyci0n6pQ_60_0_0.jpg", image_array );    
    image_height = 418
    image_width = 418   

    for x in range(0,1):
        phi = x*45
        for y in range(0,3):           
            FOV = 114
            theta = y*FOV
            theta2 = y*FOV - y*FOV/2
            print(str(theta) + "," + str(phi) )            
    

            image_array = equ.GetPerspective(FOV, theta, phi, image_height, image_width) # Specify parameters(FOV, theta, phi, height, width)        
            cv2.imwrite( perspective_path+"_"+str(FOV)+"_"+str(theta)+"_"+str(phi)+".jpg", image_array );            
            image_array = equ.GetPerspective(FOV, -1*theta, phi, image_height, image_width) # Specify parameters(FOV, theta, phi, height, width)        
            cv2.imwrite( perspective_path+"_"+str(FOV)+"_"+str(-theta)+"_"+str(phi)+".jpg", image_array );            

            image_array = equ.GetPerspective(FOV, theta2, phi, image_height, image_width) # Specify parameters(FOV, theta, phi, height, width)        
            cv2.imwrite( perspective_path+"_"+str(FOV)+"_"+str(theta2)+"_"+str(phi)+".jpg", image_array );            
            image_array = equ.GetPerspective(FOV, -1*theta2, phi, image_height, image_width) # Specify parameters(FOV, theta, phi, height, width)        
            cv2.imwrite( perspective_path+"_"+str(FOV)+"_"+str(-theta2)+"_"+str(phi)+".jpg", image_array );            


            image_array = equ.GetPerspective(FOV, theta, -1*phi, image_height, image_width) # Specify parameters(FOV, theta, phi, height, width)        
            cv2.imwrite( perspective_path+"_"+str(FOV)+"_"+str(theta)+"_"+str(-1*phi)+".jpg", image_array );            
            image_array = equ.GetPerspective(FOV, -1*theta, -1*phi, image_height, image_width) # Specify parameters(FOV, theta, phi, height, width)        
            cv2.imwrite( perspective_path+"_"+str(FOV)+"_"+str(-theta)+"_"+str(-1*phi)+".jpg", image_array );                        

            image_array = equ.GetPerspective(FOV, theta2, -1*phi, image_height, image_width) # Specify parameters(FOV, theta, phi, height, width)        
            cv2.imwrite( perspective_path+"_"+str(FOV)+"_"+str(theta2)+"_"+str(-1*phi)+".jpg", image_array );            
            image_array = equ.GetPerspective(FOV, -1*theta2, -1*phi, image_height, image_width) # Specify parameters(FOV, theta, phi, height, width)        
            cv2.imwrite( perspective_path+"_"+str(FOV)+"_"+str(-theta2)+"_"+str(-1*phi)+".jpg", image_array ); 

if __name__ == '__main__':

    #dir_index = 0
    #i = 0
    download_dir = '/home/bluesky/project/LSGI552/download/download/'
    dir_list = os.listdir(download_dir)
    for dir in dir_list:
        #if dir_index > 0:
        #    break
        #dir_index = dir_index + 1    
        for fullpath in glob.glob(download_dir+dir+"/*.jpg"):

            print(fullpath)
            #if i > 0:
            #    continue

            #print(fullpath , os.path.dirname(fullpath), os.path.basename(fullpath))
            filename, file_extension = os.path.splitext(os.path.basename(fullpath))
            print(filename,file_extension)
            if  not os.path.exists(os.path.dirname(fullpath) + "/perspective/"):
                os.mkdir(os.path.dirname(fullpath) + "/perspective/")
            perspective_path = os.path.dirname(fullpath) + "/perspective/" + filename
            makeEquirectangular(fullpath, perspective_path)
            #i = i + 1

