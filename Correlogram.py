import cv2
import os
import json
import time

def load_images_from_folder(folder):
	images = {}
	for filename in os.listdir(folder):
		img = cv2.imread(os.path.join(folder,filename))
		if img is not None:
			images[filename] = img
	return images

def bin_count():
	name = {}
	count = 0
	for i in range(4):
		for j in range(4):
			for k in range(4):
				name[str(i)+str(j)+str(k)] = count
				count+=1
	return name

def col_index(name, a):
	i = 0
	j = 0
	k = 0
	if(a[0] >= 0 and a[0] <= 63) :
		i = 0
	elif(a[0] >= 64 and a[0] <= 127) :
		i = 1
	elif(a[0] >= 64 and a[0] <= 127) :
		i = 2
	else:
		i = 3
	if(a[1] >= 0 and a[1] <= 63) :
		j = 0
	elif(a[1] >= 64 and a[1] <= 127) :
		j = 1
	elif(a[1] >= 64 and a[1] <= 127) :
		j = 2
	else:
		j = 3
	if(a[2] >= 0 and a[2] <= 63) :
		k = 0
	elif(a[2] >= 64 and a[2] <= 127) :
		k = 1
	elif(a[2] >= 64 and a[2] <= 127) :
		k = 2
	else:
		k = 3
	return name[str(i)+str(j)+str(k)]

def compress(name, a):
	res = []
	for i in range(len(a)):
		tmp = []
		for j in range(len(a[i])):
			tmp.append(col_index(name, a[i][j]))
		res.append(tmp)
	return res

def compute(a, d):
	res = [[0 for i in range(2)] for j in range(64)]
	c = 64*[0]
	for i in range(len(a)):
		for j in range(len(a[i])):
			c[a[i][j]]+=1
			tmp = 2*[0]
			for k in range(1,d+1):
				count = 0
				tot = 0
				try:
					if(a[i-k][j] == a[i][j]):
						count+=1
					tot+=1
				except Exception as e:
					pass
				try:
					if(a[i+k][j] == a[i][j]):
						count+=1
					tot+=1
				except Exception as e:
					pass
				try:
					if(a[i][j-k] == a[i][j]):
						count+=1
					tot+=1
				except Exception as e:
					pass
				try:
					if(a[i][j+k] == a[i][j]):
						count+=1
					tot+=1
				except Exception as e:
					pass
				try:
					if(a[i-k][j-k] == a[i][j]):
						count+=1
					tot+=1
				except Exception as e:
					pass
				try:
					if(a[i+k][j+k] == a[i][j]):
						count+=1
					tot+=1
				except Exception as e:
					pass
				try:
					if(a[i+k][j-k] == a[i][j]):
						count+=1
					tot+=1
				except Exception as e:
					pass
				try:
					if(a[i-k][j+k] == a[i][j]):
						count+=1
					tot+=1
				except Exception as e:
					pass
				tmp[k-1] = count/tot
			res[a[i][j]][0]+=tmp[0]
			res[a[i][j]][1]+=tmp[1]
	for i in range(64):
		if(c[i]!=0):
			res[i][0]=res[i][0]/c[i]
			res[i][1]=res[i][1]/c[i]
	return res

def cal_similarity(a,b):
	sim = 0
	for j in range(2):
		for i in range(64):
			sim+=abs(a[i][j]-b[i][j])/(1+a[i][j]+b[i][j])
	return sim/64

def process_queries(image_data):
	f = open('output0.txt', 'a+')
	counter = 1
	for filename in os.listdir('train/query'):
		start = time.time()
		file = open('train/query/'+filename, 'r')
		line = file.readline()
		line = line.split(' ')[0].split('oxc1_')[1]
		line += '.jpg'
		a = image_data[line]
		answer = {}
		print('Computing similarity for query',counter)
		for key in image_data:
			answer[key] = cal_similarity(a, image_data[key])
		print('Computing similarity Done....')
		answer = sorted(answer.items(), key = lambda kv:(kv[1], kv[0]))
		f.write('Query '+str(counter)+' For Image '+line+'\n')
		for i in range(111):
			f.write('	'+answer[i][0]+'\n')
		print(counter, 'queries processed')
		end = time.time()
		print('Time Taken ',end - start, ' seconds')
		counter+=1

if __name__ == '__main__':
	s = time.time()
	if(os.path.getsize('data.txt') > 0):
		with open('data.txt','r') as file:
			image_data = json.load(file)
	else:
		start = time.time()
		print('Loading Images ......')
		images = load_images_from_folder('images')
		print('Images Loading Done......')
		end = time.time()
		print('Time Taken ',end - start, ' seconds')

		name = bin_count()
		print('Naming Done......')

		compress_image_data = {}
		image_data = {}

		start = time.time()
		print('Compressing......')
		counter = 1
		for key in images:
			compress_image_data[key] = compress(name, images[key])
			print(counter,'Images Compressed...')
			counter+=1
		print('Compressing Done......')
		end = time.time()
		print('Time Taken ',end - start, ' seconds')

		start = time.time()
		print('Computing Distance Probability Matrix......')
		counter = 1
		for key in compress_image_data:
			image_data[key] = compute(compress_image_data[key], d=2)
			print(counter,'Images Computed...')
			counter+=1
		print('Computing Done......')
		end = time.time()
		print('Time Taken',end - start, ' seconds')

		with open('data.txt','w') as file:
			json.dump(image_data, file)
		print('Storing Done......')
	# print(image_data)
	start = time.time()
	print('Queries Processing Starting.....')
	process_queries(image_data)
	end = time.time()
	print('Time Taken for processing all queries',end - start, ' seconds')
	e = time.time()
	print('Total Time Taken',e - s, ' seconds')