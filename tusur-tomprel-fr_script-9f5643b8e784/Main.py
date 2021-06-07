import logging
import sys, traceback
import threading
from time import sleep 
from scipy.spatial import distance
import FaceRecognition.winter as winter
import FaceRecognition.DescriptorKeeper as DK
import FaceRecognition.SelectData as sd






def rec():

	FACE_REC_LIM = 0.6 #reccomended by developers of dlib
	image_face_descriptor = DK.returnDescriptor(winter.accept_file()) #получаем входное изображение и возвращаем его дескриптор
	
	# проверяем а система хотя бы нашла лицо, если нет (-1), то оформляет ответ "-1" в html формате
	if image_face_descriptor == -1:

		htmlstr = '<!DOCTYPE html><html><head></head><body><h1>' + str(image_face_descriptor) + '</h1></body></html>' 

		#сбор данных
		sd.selectData()
	# если лицо определено и вернулся нормальный дескриптор 	
	else:
		
		bench_face_kit = DK.getBenchKit() # изымаем эталонные из папки храения

		# """вычисляем евклидово расстояние и сравниваем с предельным значением и 
		# если хотя бы один эталонный дескриптор совпал с входным выходим из цикла """
		for bench_face_descriptor in bench_face_kit:
			euclidean = distance.euclidean(bench_face_descriptor, image_face_descriptor)
			if euclidean < FACE_REC_LIM:
				out_value = 1
				break
			else:
				out_value = 0
		
		# оформляем полученный ответ либо 0 (не пропустить чужого) либо 1 (пропутить своего) в html
		htmlstr = '<!DOCTYPE html><html><head></head><body><h1>' + str(out_value) + '</h1></body></html>' 

		#сбор данных
		sd.selectData(out_value, euclidean)

	winter.send_head(ctype = winter.FT_HTML, clength = len(htmlstr)) # хз че это
	winter.return_answer(htmlstr) # возвращаем ответ 

def index():
	winter.return_file('examples/index.html', winter.FT_HTML)

def snifer():
	winter.accept_file()
	#while(True):
	winter.return_file('examples/index.html', winter.FT_HTML)


#config
cfg_LogFormat = logging.Formatter(fmt='[%(asctime)s]-%(levelname)s-%(name)s: %(message)s', datefmt='%d-%b-%Y %H:%M:%S')

#logger create
log = logging.getLogger()
log_strm_hndl = logging.StreamHandler()

log_strm_hndl.setLevel(logging.INFO)
log_strm_hndl.setFormatter(cfg_LogFormat)
log.setLevel(logging.DEBUG)
log.addHandler(log_strm_hndl)



try:
	log.debug('Start')
	winter.add_handler('/rec', rec)
	winter.add_handler('/', index)
	winter.add_handler('/snif', snifer)
	winter.http_server_start()
	#winter.call_handler('test')
	#while winter._server_thread.is_alive():
	#	sleep(1)
	#	print('myiter == ' + str(myiter))
	while(winter.http_server_isruning()):
		sleep(3)

except:
	log.error("Critical exception\n"+\
				str(traceback.print_exc(limit=2, file=sys.stdout)))
finally:
	winter.http_server_stop()
	log.debug('End')



