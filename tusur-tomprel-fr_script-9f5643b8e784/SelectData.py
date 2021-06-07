import datetime 

# вызываем функцию сбора данных в Main хотя она нахер не нужна, потому что Влад уже логами сделал сбор данных, единственное только что евклидово расстояние регистрировать
def selectData(answer=-1, distance='not defined'):

    file = open("statistics.txt", 'a')
    file.write("_________________________________________\n")
    file.write('Time: {}'.format(datetime.datetime.now()) + "\n")
    file.write('Eucledian distance: {}'.format(distance) + "\n")
    file.write('Answer: {}'.format(answer) + "\n")
    file.write("_________________________________________" + "\n")
    file.close()



