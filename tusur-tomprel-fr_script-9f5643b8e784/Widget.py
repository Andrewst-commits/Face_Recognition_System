from tkinter import *
from time import sleep
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import FaceRecognition.DescriptorKeeper as DK

 



class MainWindow:

     def __init__(self, title="Access Control System", size='450x200+300+250'):

        #создаем главное окно
        self.master = Tk()
        self.master.geometry(size)
        self.master.title(title)

        #создаем индикатор процесса создания дескриптора (это не относится к индикации со светодиодами это другое)
        self.progressBar = ttk.Progressbar(self.master, orient=HORIZONTAL, length=300, mode="determinate")
        self.progressBar.grid(row=2, column=0, columnspan=2, sticky=E, pady=15, padx=22 )

        #метка, что нужно выбрать эталоны
        self.label = Label(text="Choose benchmark files:")
        self.label.grid(row=0, column=0, sticky=W, padx=20, pady=10, ipady=10)

        #метка что нужно выбрать директорию хранения(keepeing directory)
        self.label = Label(text="Set storage path:")
        self.label.grid(row=1, column=0, sticky=W, padx=20, pady=10)

        #метка выполнено действие или нет
        self.labelDone_1 = Label(text="---") 
        self.labelDone_1.grid(row=0, column=2)

        #метка выполнено действие или нет
        self.labelDone_2 = Label(text="---")
        self.labelDone_2.grid(row=1, column=2)

        #обзор файлов для выбора эталонов
        self.viewBut = Button(self.master, text="View", width=10)
        self.viewBut["command"] = self.getFiles
        self.viewBut.grid(row=0, column=1)

        #обзор папок для выбора директории хранения
        self.viewBut = Button(self.master, text="View", width=10)
        self.viewBut["command"] = self.getDir
        self.viewBut.grid(row=1, column=1)
        
        #выйти из приложения
        self.cancelBut = Button(self.master, text="Cancel", width=10)
        self.cancelBut["command"] = self.master.destroy
        self.cancelBut.grid(row=3, column=2)

        #создать и добавить дескрипторы
        self.addBut = Button(self.master, text="Add", width=10)
        self.addBut["command"] = self.addDescriptors
        self.addBut.grid(row=3, column=1, pady=5)  

        self.benchmarkFiles = None
        self.directory = None
    
     def getFiles(self):

         self.benchmarkFiles = fd.askopenfilenames(filetypes=(("jpg files", "*.jpg"),)) #загружвем эталоны (только jpg)
         
         #если выбрали файлы то Done
         if self.benchmarkFiles:     
            self.labelDone_1["text"] = "Done"
            return 0

         #если нажали отмена
         self.labelDone_1["text"] = "---"
  

     def getDir(self):

         self.directory = fd.askdirectory() #выбираем папку хранния
         
         # если она выбрана 
         if self.directory:

            # точно эту папку? если yes (true) то Done если no (false), то --- и обращаем directory в none (тип передумал выбирать)
            answer = mb.askyesno(title="To choose the directory", message=self.directory)
            if answer: 
                self.labelDone_2["text"] = "Done"
                return 0
            else:
               self.directory = None
               self.labelDone_2["text"] = "---"

         #если нажали отмена
         self.labelDone_2["text"] = "---"
      
     # ну это я думаю понятно
     def cancel(self):
         self.master.destroy()

     def addDescriptors(self):

         # если все параметры выбраны запускаем индикатор процесса и на второй итерации сохраняем дескрипторы
         if self.benchmarkFiles and self.directory:

            for i in range(20):
                sleep(0.1)
                self.progressBar['value'] += 5 
                self.master.update_idletasks()
                if i == 2:
                    DK.saveDescriptor(self.benchmarkFiles, self.directory)
            mb.showinfo("Info", "Descriptors are created successfully!")
            self.master.destroy()
         else:
             mb.showerror("Error", "Set all parameters!")

     # это тоже понятно
     def run(self):
          self.master.mainloop() 
    
# и это
if __name__ == "__main__":  
    
    block = MainWindow() 
    block.run() 




        


       




