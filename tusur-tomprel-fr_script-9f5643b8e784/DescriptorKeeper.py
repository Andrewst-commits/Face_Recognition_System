from numpy import save, load
from glob import glob
from os import listdir
from scipy.spatial import distance
from dlib import shape_predictor
from dlib import face_recognition_model_v1
from dlib import get_frontal_face_detector, load_rgb_image



detector = get_frontal_face_detector()
shape_predictor = shape_predictor('Models/shape_predictor_68_face_landmarks.dat') 
recognizer = face_recognition_model_v1('Models/dlib_face_recognition_resnet_model_v1.dat') 

              
    
def returnDescriptor(picturePath):

    shape = -1 # тут -1 подчеркивает что в shape не вернулось описанное лицо и при shape = -1 вернется -1
    picture = load_rgb_image(picturePath) # подаем в функцию путь к фотографии и извлекаем ее
    detected = detector(picture, 0) # проходит по всей фотографии и ищет лицо, затем записывает его место положение в detected
    for d in detected: 
        #print("Detection: Left: {} Top: {} Right: {} Bottom: {}".format(d.left(), d.top(), d.right(), d.bottom())) коордтнаты прямоугольника
        shape = shape_predictor(picture, d) # определяет уникальные точки лица и записывает описанное лицо в shape

    if shape == -1:
        return -1 # такое значение возвращается в том случае если shape_predictor не вернул в shape описанное лицо(то есть фотка была смазана и система не нашла на ней лица)

    return recognizer.compute_face_descriptor(picture, shape)  # создает многомерный вектор из shape
    
             
# вызывается только в Widget и нужна лишь для настройки системы распознавания
def saveDescriptor(picturePaths, directory):

    file = open("keeping_dir.txt", "w") # это txt файл где хранится полный путь к место, где будут храниться эталонные дескрипторы
    file.write(directory)
    file.close()

    counter = len(listdir(directory)) + 1 # хранит число = количество файлов + 1 (это нужно чтобы отображался номер нового дескриптора)
    for picturePath in picturePaths: # получаем список путей эталонных фото
        
        #формирование полного пути будущего дескриптора, включая его название
        path = directory + "/BenchmarkDescriptor_" 
        path = path + str(counter)
        
        # посылем текущий путь эталонного фото(мы в цикле), создаем его дескриптор и сохраняем его по сформированнному пути
        save(path, returnDescriptor(picturePath))
        counter += 1

#вызывается исключительно при идентификации входного лица 
def getBenchKit():

    kit = [] 
    keeping_directory = open("keeping_dir.txt") #извлекаем из txt файла директорию, хранящую дескрипторы
    bech_descriptors = glob(str(keeping_directory.read()) + "/*.npy") # извлекаем список путей файлов с раширением npy (дескрипторов)
    keeping_directory.close()

    for i in  bech_descriptors:
        kit.append(load(i)) # извлекаем дескрипторы из файлов в список

    return kit #возвращаем эталонные дескрипторы 







 

