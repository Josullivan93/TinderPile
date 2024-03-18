# Python App for Rapid Classification of Piling Images
import os, glob
import tkinter as tk
import csv
import shutil
from random import sample
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

class App:
    def __init__(self, tkWindow = tk.Tk()):

        # Create Window - Name & Size
        self.tkWindow = tkWindow
        self.tkWindow.title("Piling Classification")
        self.tkWindow.geometry("{}x{}".format(1290,840))

        # Bind Arrow Keys to swipe directions & escape to exit
        self.tkWindow.bind("<Left>", self.swipe_nopile)
        self.tkWindow.bind("<Right>", self.swipe_pile)
        self.tkWindow.bind("<Up>", self.swipe_edge)
        self.tkWindow.bind("<Down>", self.swipe_skip)
        self.tkWindow.bind("<Escape>", self.close)
        self.tkWindow.bind("q", self.close)

        # Create Variables
        self.is_active = True
        self.next_img = tk.IntVar()
        self.dir_path = tk.StringVar()
        self.img_path = tk.StringVar()
        self.samp_num = tk.DoubleVar()
        self.samp_num.set("10")
        self.samp_opt_val = tk.StringVar(self.tkWindow)
        self.samp_opt_val.set("%")
        self.samp_opt_list = ["%", "Samples"]

        # Create Frames for Image display and Option selection
        self.img_frame = tk.Frame(self.tkWindow,background = "gray2", width = 1280, height = 720)
        self.opt_frame = tk.Frame(self.tkWindow, width = 1280, height = 50)
        self.go_frame = tk.Frame(self.tkWindow, width = 1280, height = 50)

        # Set layout of frames
        self.tkWindow.grid_rowconfigure(0, weight=1)
        self.tkWindow.grid_columnconfigure(0, weight=1)
        
        self.img_frame.grid(row=0, sticky="nsew")
        self.opt_frame.grid(row=1, sticky="n", pady= 5)
        self.go_frame.grid(row=2, pady= 5)

        # Create Image Widget
        self.img_lab = tk.Label(self.img_frame)

        # Layout Img Widget
        self.img_lab.grid(row = 0, column = 0)

        # Create Option Widgets
        self.wrk_dir_btn = ttk.Button(self.opt_frame, text = "Select Image Folder", command = self.select_folder)
        # sample size: text label
        self.sample_label = ttk.Label(self.opt_frame, text="Sample Size: ")
        # Text entry for sample number/percentage
        self.sample_num = ttk.Entry(self.opt_frame, textvariable = self.samp_num, width = 10 )
        # dropdown select total images / percent of images 
        self.sample_opt = ttk.OptionMenu(self.opt_frame, self.samp_opt_val , self.samp_opt_val.get() ,*self.samp_opt_list)

        # Layout Opt Widget
        self.wrk_dir_btn.grid(row = 0, column = 0, padx=10)
        self.sample_label.grid(row = 0, column = 1, padx=5)
        self.sample_num.grid(row = 0, column = 2)
        self.sample_opt.grid(row = 0, column = 3, padx=2)
        
        # start button with state default to disabled. Enabled in select_folder function
        self.go_btn = ttk.Button(self.go_frame, text = "Start!", state="disabled", command = self.go_fun)

        self.go_btn.grid(row=0,column=3)

        self.wrk_dir_btn.wait_variable(self.dir_path)

        self.go_btn.config(state="enabled")

        self.tkWindow.mainloop()
        
    
    # select folder command
    def select_folder(self):
        self.dir_path.set(tk.filedialog.askdirectory(title = "Select Image Folder"))
        os.chdir(self.dir_path.get())
        print("Accessing Folder: ", self.dir_path.get())
        
    def go_fun(self):
        # Check if csv exists & create if not
        if not os.path.isfile(os.path.join(self.dir_path.get(), 'annotation_out.csv')):
            with open('annotation_out.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Directory", "Pile_Name", "Image_ID", "Category", "Cat_Change"])

        # List files in current directory
        self.file_list = glob.glob('*.jpg' , recursive=False)
        #print(self.file_list)
        
        self.file_unique = list(set(["_".join(file.split("_", 3)[:3]) for file in self.file_list]))
        print("Unique Files: ", len(self.file_unique))

        #loop through unique names
        for file_string in self.file_unique:

           # get files containing the unique substring
            file_match = [i for i in self.file_list if file_string in i]

           # subsample based on number or percentage (if/else)
            if self.samp_opt_val.get() == "%":
                snum = round((float(self.samp_num.get())/100)*len(file_match))

            elif self.samp_opt_val.get() == "Samples":
                snum = round(float(self.samp_num.get()))

            if snum < 1 : snum = 1
            img_sample = sample(file_match, k = snum)
            print(img_sample)

            for self.img in img_sample:
                self.img_path.set(os.path.join(self.dir_path.get(), self.img))
                self.load_img()
                self.tkWindow.wait_variable(self.next_img)
            
        print("End of files.")
        self.close()
    
    def load_img(self):
        # Update the image
        self.ann_image = ImageTk.PhotoImage(Image.open(self.img_path.get()).resize((1280,720)))
        # Update image holder
        self.img_lab.config(image=self.ann_image)
        # Set "trigger" to wait for user swipe 
        self.next_img.set(0)

    def swipe_nopile(self, event):
        # Move to No_Pile Directory & Add details to CSV
        # Get pile name, image Id and current category
        pile_name = "_".join(self.img.split("_", 3)[:3])
        img_id = self.img.split("_", 3)[3].split(".")[0]
        if self.img.split("_", 1)[0] == "NonPile":
            img_cat = 0
        else:
            img_cat = 1

        with open('annotation_out.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.dir_path.get(), pile_name, img_id, "NonPile", img_cat])  

        try:
            shutil.move(
                self.img_path.get(),
                os.path.join(self.dir_path.get(), 'NonPile', self.img))
        
        except FileNotFoundError:
            os.mkdir(os.path.join(self.dir_path.get(), 'NonPile'))
            shutil.move(
                self.img_path.get(),
                os.path.join(self.dir_path.get(), 'NonPile', self.img))
        # Set "trigger" to load next image
        self.next_img.set(1)

    def swipe_pile(self, event):
        # Move to Pile Directory & Add details to CSV
        # Get pile name, image Id and current category
        pile_name = "_".join(self.img.split("_", 3)[:3])
        img_id = self.img.split("_", 3)[3].split(".")[0]
        if self.img.split("_", 1)[0] == "Pile":
            img_cat = 0
        else:
            img_cat = 1

        with open('annotation_out.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.dir_path.get(), pile_name, img_id, "Pile", img_cat])  

        try:
            shutil.move(
                self.img_path.get(),
                os.path.join(self.dir_path.get(), 'Pile', self.img))
        
        except FileNotFoundError:
            os.mkdir(os.path.join(self.dir_path.get(), 'Pile'))
            shutil.move(
                self.img_path.get(),
                os.path.join(self.dir_path.get(), 'Pile', self.img))
            
        # Set "trigger" to load next image
        self.next_img.set(1)

    def swipe_edge(self, event):
        # Move to No_Pile Directory & Add details to CSV
        # Get pile name, image Id and current category
        pile_name = "_".join(self.img.split("_", 3)[:3])
        img_id = self.img.split("_", 3)[3].split(".")[0]
        img_cat = "NA"

        with open('annotation_out.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.dir_path.get(), pile_name, img_id, "Edge", img_cat])  

        try:
            shutil.move(
                self.img_path.get(),
                os.path.join(self.dir_path.get(), 'Edge', self.img))
        
        except FileNotFoundError:
            os.mkdir(os.path.join(self.dir_path.get(), 'Edge'))
            shutil.move(
                self.img_path.get(),
                os.path.join(self.dir_path.get(), 'Edge', self.img))
            
        # Set "trigger" to load next image
        self.next_img.set(1)

    def swipe_skip(self, event):
        # Move to No_Pile Directory & Add details to CSV
        # Get pile name, image Id and current category
        pile_name = "_".join(self.img.split("_", 3)[:3])
        img_id = self.img.split("_", 3)[3].split(".")[0]
        img_cat = "NA"

        with open('annotation_out.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.dir_path.get(), pile_name, img_id, "Skip", img_cat])  

        try:
            shutil.move(
                self.img_path.get(),
                os.path.join(self.dir_path.get(), 'Skip', self.img))
        
        except FileNotFoundError:
            os.mkdir(os.path.join(self.dir_path.get(), 'Skip'))
            shutil.move(
                self.img_path.get(),
                os.path.join(self.dir_path.get(), 'Skip', self.img))
        # Set "trigger" to load next image
        self.next_img.set(1)

    def close(self, *args):
        print('Closing...')
        self.tkWindow.destroy()

if __name__ == '__main__':

    app = App()