import os
import sys

path = "anteater5"

file_list = os.listdir(path)
for file in file_list:
	file_abs_path = os.path.join(path, file)
	if not os.path.isdir(file_abs_path):
		strs = file.split('_')
		strs[1] = strs[1].zfill(3)
		#print(strs)
		newName = '_'.join(strs)
		os.rename(path + "/" + file, path + "/" + newName)


#    newname = "emoji_"+filename
#    os.rename(path+"\\"+filename , "D:\new_emojis"+"\\"+newname)