import subprocess
import os
import signal
import os
import time
import argparse
from datetime import date

print(date.today().strftime("%b-%d-%Y"))


import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import scrolledtext

from PIL import Image, ImageEnhance, ExifTags, ImageFilter
from PIL.ExifTags import TAGS

from pillow_heif import register_heif_opener
import pillow_heif
register_heif_opener()

import numpy as np
from glob import glob
import random
from time import time
import os

from PIL import ImageTk,Image 

from utils import *


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry('1200x800') # adjust window size here
        self.master.title("Image Mosaic")
        self.grid(column=0, row=0, padx=10, pady=2, sticky="W")

        # set formatting parameters for the interface
        self.col2width = 25 
        self.preview_size = 700

        # Initialize starting trial name and save directory
        self.image_dir = "BACKGROUND DIRECTORY"
        self.main_image_name = "MAIN IMG"
        self.save_name = "SAVE PATH"

        # set the defaults for the image mosaic
        self.min_image_dim = 2000
        self.tile_image_size = 100
        self.alpha = 0.15
        self.blur = 2
        self.sharpness = 1

        # initialize the image arrays
        self.main_image = init_main_image(resource_path("main_test.png"), self.min_image_dim)
        self.background = init_main_image(resource_path("background_test.png"), self.min_image_dim)
        self.background_array = None # Used to store the background before cropping
        self.temp_image = None # This is what gets saved
        self.get_new_dims()
        self.background_starter_list = []

        # set the color mode for the images
        self.bg_mode = "bw"
        self.fg_mode = "color"


        self.create_widgets()

    def create_widgets(self):
        row_id = 0

        # PREVIEW IMAGE
        # print(self.main_image.size, self.background.size)
        self.blend_mosaic(from_array=False)
        self.update_preview(self.temp_image)      

        # BUTTON to specify the MAIN image
        self.chg_main_img = tk.Button(self,fg="black",
                                      text="Select Main Image",
                                      command=self.get_main_image, bg='#ffffa5')
        self.chg_main_img.grid(column=0, row=row_id, padx=2,pady=2,sticky="W")
        self.chg_main_img_lbl = tk.Label(self, text=self.main_image_name[-self.col2width:], width=self.col2width, height=1, anchor="e")
        self.chg_main_img_lbl.grid(column=1, row=row_id, padx=0, pady=2,sticky="W")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        # BUTTON to specify the load directory
        self.chg_background_dir = tk.Button(self,fg="black",
                                      text="Background Directory",
                                      command=self.get_background_dir, bg='#ffffa5')
        self.chg_background_dir.grid(column=0, row=row_id, padx=2,pady=2,sticky="W")
        self.chg_background_dir_lbl = tk.Label(self, text=self.image_dir[-self.col2width:], width=self.col2width, height=1, anchor="e")
        self.chg_background_dir_lbl.grid(column=1, row=row_id, padx=0, pady=2,sticky="W")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        # TEXT INPUT for image dimensions
        self.set_img_dims = tk.Label(self,fg="black",
                                      text="Min Image Dimension:   ")
        self.set_img_dims.grid(column=0, row=row_id, padx=2,pady=2,sticky="W")
        # self.set_img_dims_lbl = tk.Text(self,height=1,width=10,bg='#E6E6E3') # SWITCH TO ENTRY
        self.set_img_dims_lbl = tk.Entry(self,width=10, justify="right", bg='#E6E6E3')
        self.set_img_dims_lbl.insert(INSERT, "{:>10}".format(str(self.min_image_dim)))
        self.set_img_dims_lbl.grid(column=1, row=row_id, padx=0, pady=2,sticky="E")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        # TEXT INPUT for tile dimensions
        self.set_tile_dims = tk.Label(self,fg="black",
                                      text="Tile Image Dimension:")
        self.set_tile_dims.grid(column=0, row=row_id, padx=2,pady=2,sticky="W")
        self.set_tile_dims_lbl = tk.Entry(self,width=10, justify="right", bg='#E6E6E3')
        self.set_tile_dims_lbl.insert(INSERT, "{:>10}".format(str(self.tile_image_size)))
        self.set_tile_dims_lbl.grid(column=1, row=row_id, padx=0, pady=2,sticky="E")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        # TEXT INPUT for alpha
        self.alpha = 0.25
        self.set_alpha = tk.Label(self,fg="black",
                                      text="Alpha:")
        self.set_alpha.grid(column=0, row=row_id, padx=2,pady=2,sticky="W")
        self.set_alpha_lbl = tk.Entry(self,width=10, justify="right", bg='#E6E6E3')
        self.set_alpha_lbl.insert(INSERT, "{:>10}".format(str(self.alpha)))
        self.set_alpha_lbl.grid(column=1, row=row_id, padx=0, pady=2,sticky="E")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        # TEXT INPUT for blur
        self.set_blur = tk.Label(self,fg="black",
                                      text="Blur:")
        self.set_blur.grid(column=0, row=row_id, padx=2,pady=2,sticky="W")
        self.set_blur_lbl = tk.Entry(self,width=10, justify="right", bg='#E6E6E3')
        self.set_blur_lbl.insert(INSERT, "{:>10}".format(str(self.blur)))
        self.set_blur_lbl.grid(column=1, row=row_id, padx=0, pady=2,sticky="E")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        # TEXT INPUT for sharpness
        self.set_sharpness = tk.Label(self,fg="black",
                                      text="Sharpness:")
        self.set_sharpness.grid(column=0, row=row_id, padx=2,pady=2,sticky="W")
        self.set_sharpness_lbl = tk.Entry(self,width=10, justify="right", bg='#E6E6E3')
        self.set_sharpness_lbl.insert(INSERT, "{:>10}".format(str(self.sharpness)))
        self.set_sharpness_lbl.grid(column=1, row=row_id, padx=0, pady=2,sticky="E")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        # BUTTON to refresh
        self.refresh_frame = tk.Frame(self)
        self.refresh_frame.grid(column=1,columnspan = 1, row=row_id, padx=2,pady=10, sticky="E")
        
        self.refresh_button = tk.Button(self.refresh_frame,fg="black",
                                 text="Refresh",
                                 command=self.refresh)
        self.refresh_button.grid(column=1,columnspan = 1, row=0, padx=2,pady=2, sticky="E")
        self.random_refresh_val = IntVar()
        self.random_refresh_val.set(1)
        self.random_refresh = tk.Checkbutton(self.refresh_frame,fg="black",
                                 text="Random Tile", variable=self.random_refresh_val)
        self.random_refresh.grid(column=0,columnspan = 1, row=0, padx=2,pady=2, sticky="E")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        # BUTTON to specify the save directory
        self.chg_save_dir = tk.Button(self,fg="black",
                                      text="Save Image Mosaic",
                                      command=self.get_save_dir, bg='#ffffa5')
        self.chg_save_dir.grid(column=1, columnspan=1, row=row_id, padx=2, pady=2, sticky="E")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        self.filler = tk.Label(self, text=" ")
        self.filler.grid(column=0, row=row_id, padx=2,pady=50,sticky="W")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        # STATS for total images
        self.image_count = tk.Label(self,fg="black",text="Image Count: XX")
        self.image_count.grid(column=0, row=row_id, padx=2,pady=2,sticky="W")

        # STATS for final image size
        self.image_size_text = tk.Label(self,fg="black",text="Final Image Size: " + str(self.new_dims))
        self.image_size_text.grid(column=1, row=row_id, padx=2,pady=2,sticky="W")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        # STATS for final image size
        self.background_image_count = tk.Label(self,fg="black",text="Background Tiles: XX")
        self.background_image_count.grid(column=0, row=row_id, padx=2,pady=2,sticky="W")

        row_id +=1 #### #### #### NEW ROW #### #### #### NEW ROW #### #### ####

        # self.progress_bar = tk.Text(self, height=1,width=int(self.col2width*1.5),state=DISABLED)
        self.progress_bar_desc = tk.Label(self,fg="black", text="Status: Ready")
        self.progress_bar_desc.grid(column=0, row=row_id, padx=0, pady=2,sticky="W")
        self.progress_bar = Progressbar(self, orient = HORIZONTAL,
                                        length = int(self.col2width*8), mode = 'determinate')
        self.progress_bar.grid(column=1, row=row_id, padx=0, pady=2,sticky="W")


        # # POWER OFF BUTTON
        # self.quit = tk.Button(self, text="Exit", fg="red",
        #                       command=self.master.destroy)
        # self.quit.grid(column=2, row=0, padx=0,pady=2,sticky="e")


    def refresh(self):
        # Check the tile sizes and update the background if it changes
        old_tile_size = self.tile_image_size
        self.tile_image_size = int(self.set_tile_dims_lbl.get())
        if self.tile_image_size != old_tile_size:
            self.get_main_image(path = self.main_image_name)
            self.get_background_dir(self.image_dir)
        elif bool(self.random_refresh_val.get()):
            self.update_background()
        # Check the main image size and update it if changes
        old_img_size = self.min_image_dim
        self.min_image_dim = int(self.set_img_dims_lbl.get())
        if self.min_image_dim != old_img_size:
            self.get_main_image(path = self.main_image_name)

        # Update the alpha, sharpness, and blur values
        self.alpha = float(self.set_alpha_lbl.get())
        self.blur = float(self.set_blur_lbl.get())
        self.sharpness = float(self.set_sharpness_lbl.get())
        # blend
        self.blend_mosaic(from_array=False)

    def get_save_dir(self):
        # self.chg_save_dir_lbl['text'] = self.save_dir
        self.save_name = filedialog.asksaveasfile(mode="w", defaultextension=".png")
        if self.save_name is None:
            return
        if self.save_name.name[-3:] in ["png","PNG"]:
            self.temp_image.save(self.save_name.name)
        else:
            self.temp_image.save(self.save_name.name + '.png')
        
    def open_popup(self, title, message):
        top= Toplevel(self)
        top.geometry("250x250")
        top.title(title)
        Label(top, text= message, font=('Mistral 18 bold')).place(x=150,y=80)  


    def get_main_image(self, path = None):
        # get the main image
        if path is None:
            self.main_image_name = filedialog.askopenfilename(title="Select the Main Image")
        if self.main_image_name is None:
            return

        self.chg_main_img['bg'] = "green"
        self.chg_main_img_lbl['text'] = self.main_image_name
        # replace the temp image 
        self.main_image = Image.open(self.main_image_name)
        # Correct the orientation
        self.main_image = correct(self.main_image)

        # Get new dimensions and then update the preview
        self.min_image_dim = int(self.set_img_dims_lbl.get())
        self.get_new_dims()
        self.blend_mosaic(from_array=False)

        # Update the final image size in the interface 
        self.image_size_text['text'] = "Final Image Size: " + str(self.new_dims)


    def get_background_dir(self, path=None):
        # get the save directory
        if path is None:
            self.image_dir = filedialog.askdirectory()
        if self.image_dir is None:
            return

        # Update the text and the button color
        self.chg_background_dir['bg'] = "green"
        self.chg_background_dir_lbl['text'] = self.image_dir

        # load the background image paths
        background_image_paths = load_background_images(self.image_dir)

        # Store the background images in a starter array
        self.background_starter_list=[]
        count = 0
        self.progress_bar_update()
        for img_path in background_image_paths:
            if count % int(len(background_image_paths)/50)==0:
                # Update the progress bar
                # print("{}/{} images loaded".format(count,len(background_image_paths)))
                percent = count/len(background_image_paths)
                # print(percent, count, len(background_image_paths))
                self.progress_bar_update(percent=percent, text="Loading Imgs")
                self.image_count['text']="Image Count: " + str(len(self.background_starter_list))
                self.update()

            # resize to the tile shape before saving into the array
            tmp_img = Image.open(img_path)
            tmp_img = correct(tmp_img)
            tmp_img = self.resize_to_tile(tmp_img)

            self.background_starter_list.append(np.array(tmp_img))
            count +=1
        
        self.progress_bar_update()
        self.update()
        # Update the interface with the image count
        self.image_count['text']="Image Count: " + str(len(self.background_starter_list))
        print("Images loaded into starter array")

        # Create the background collage 
        self.update_background()

    def resize_to_tile(self, tmp_img):
        w_dim, h_dim = tmp_img.size
        h_dim = int(h_dim / w_dim * self.tile_image_size)
        w_dim = self.tile_image_size
        
        tmp_img = tmp_img.resize((w_dim,h_dim))
        return tmp_img

    def update_background(self):
        # Add some padding to the ends
        main_img_dim = [int(self.new_dims[0]*1.5), int(self.new_dims[1]*1.5)]
        # print("BACK DIMENSIONS", main_img_dim)
        # print("Collage Dimensions:", main_img_dim)
        # get the entry settings
        self.tile_image_size = int(self.set_tile_dims_lbl.get())


        collage_img = np.zeros((main_img_dim[1],main_img_dim[0],3))
        cols_full = False
        w_idx = 0
        # random.seed(42)
        count = 0

        start_time = time()
        img_list_copy=[]
        while not cols_full:
            rows_full = False
            h_idx = 0
            while not rows_full:
                row_start_time = time()
                if len(img_list_copy) == 0:
                    img_list_copy = self.background_starter_list.copy()
                    random.shuffle(img_list_copy)
                # load the image
                count +=1
                tmp_img = img_list_copy.pop() #Image.open(img_path)
                tmp_img = Image.fromarray(tmp_img)
                
                
                # check that its RGB
                if len(np.array(tmp_img).shape) ==2:
                    tmp_img = tmp_img.convert("RGB")
                if np.array(tmp_img).shape[2] == 4: 
        #             print(img_path)
                    #convert to RGB
                    background = Image.new('RGBA', tmp_img.size, (255, 255, 255))
                    tmp_img = Image.alpha_composite(background, tmp_img)
                
                # # adjust the dimensions so that it fits the row
                w_dim, h_dim = tmp_img.size
                # h_dim = int(h_dim / w_dim * self.tile_image_size)
                w_dim = self.tile_image_size
                
                # tmp_img = tmp_img.resize((w_dim,h_dim))
                
                # add variance to the height to account for batches of identical images
                height_var_adj = random.randint(0,h_dim//10)
                new_h_dim = h_dim-(2*height_var_adj)
                tmp_img = tmp_img.crop([0,height_var_adj,w_dim,h_dim-height_var_adj])
                
                # paste the black and white image to the collage
                collage_img[h_idx:h_idx+new_h_dim,w_idx:w_idx+w_dim] = np.array(tmp_img)[:,:,:3]
                
                
                # update the x index
                h_idx += new_h_dim
                if h_idx > self.new_dims[1]+self.tile_image_size:
                    rows_full = True
                    # print the progress
                    current_epoch = w_idx//self.tile_image_size+1
                    total_epochs =  (self.new_dims[0])//self.tile_image_size + 1
                    # print("Columns {}/{} Complete in {} seconds. Estimated time remaining {}".format(
                    #     current_epoch,
                    #     total_epochs,
                    #     round(time() - start_time,1),
                    #     round((time() - start_time) * ((total_epochs - current_epoch)/current_epoch),1)))
                    
                    # update the y index
                    w_idx += w_dim

                    # Update the progress bar
                    percent = current_epoch / total_epochs
                    self.progress_bar_update(percent=percent, text="Adding Tiles")
                    self.background_image_count['text'] = "Background Tiles: " + str(count)
                    self.update()
                    
                    
            # update the index
            if w_idx >= self.new_dims[0]+self.tile_image_size:
                cols_full = True

        self.progress_bar_update()
        self.update()
        # Update the count for the background tiles
        self.background_image_count['text'] = "Background Tiles: " + str(count)
        # Convert to an image and crop 
        self.background_array = collage_img

        self.blend_mosaic()

        self.update()

    def crop_background(self):
        vertical_adjustment = np.random.randint(5,20)
        horizontal_adjustment = np.random.randint(5,20)
        collage_resized = self.background_array[vertical_adjustment:self.new_dims[1]+vertical_adjustment,
                                        horizontal_adjustment:self.new_dims[0]+horizontal_adjustment]
        self.background = Image.fromarray(collage_resized.astype('uint8'), 'RGB')


    def progress_bar_update(self, percent=0, text=" "):
        # if percent == 0: 
        #     self.progress_bar = tk.Text(self, height=1,width=int(self.col2width*1.5), state='disabled')
        #     self.progress_bar.insert(INSERT,text * int(self.col2width*1.5))
        # else:
        #     right_edge = int(percent * int(self.col2width*1.5))
        #     self.progress_bar.delete(0, END)
        #     self.progress_bar.insert(INSERT, str("{:>"+str(int(self.col2width*1.5))+"}").format(text))
        #     self.progress_bar.tag_add("progress","1.0","1." + str(right_edge))
        #     self.progress_bar.tag_config("progress", background="green",
        #          foreground="black")
        if percent == 0:
            self.progress_bar['value'] = 0
            self.progress_bar_desc['text'] ="Status: Ready"
        else:
            self.progress_bar_desc['text'] ="Status: " + text
            self.progress_bar['value'] = percent * 100
            
        return True

    def update_preview(self, img):
        """Updates the interface preview"""

        # Pad the dimensions so it resizes correctly
        ratio = self.preview_size/max(img.size)
        new_size = tuple([int(x*ratio) for x in img.size])

        # Set eh background to light grey
        rgbArray = np.zeros((self.preview_size,self.preview_size,3))
        rgbArray[..., 0] = 230
        rgbArray[..., 1] = 230
        rgbArray[..., 2] = 230
        bg = Image.fromarray((rgbArray).astype('uint8'), 'RGB')


        img = img.resize(new_size)

        bg.paste(img, (int((self.preview_size - img.size[0])/2), int((self.preview_size - img.size[1])/2,)))
        img = bg

        # resize to self.preview_size X self.preview_size
        self.img_preview = img.resize((self.preview_size,self.preview_size))
        self.img_preview = ImageTk.PhotoImage(self.img_preview)
        self.img_label = tk.Label(root, image = self.img_preview)
        self.img_label.grid(column=1, row=0, padx=30, pady=10,sticky="W")

    def get_new_dims(self):
        # Pad the dimensions so it resizes correctly
        img = self.main_image.copy()
        ratio = int(self.min_image_dim)/min(img.size)
        new_size = tuple([int(x*ratio) for x in img.size])
        self.new_dims = new_size

    def blend_mosaic(self, from_array=True):
        if from_array:
            self.crop_background()
            collage_background = self.background.copy()
        else:
            collage_background = self.background.copy()

        main_img = self.main_image.copy()

        # Resize the images
        # print("AAA",self.new_dims,main_img.size)
        main_img = main_img.resize(self.new_dims)
        collage_background = collage_background.resize(self.new_dims)

        # convert to black and white
        if self.bg_mode == "bw":
            collage_background = ImageEnhance.Color(collage_background)
            collage_background = collage_background.enhance(0) 
        if self.fg_mode =='bw':
            main_img = ImageEnhance.Color(main_img)
            main_img = main_img.enhance(0)  

        main_img_adjusted = main_img.filter(ImageFilter.GaussianBlur(radius = self.blur))
        main_img_adjusted = ImageEnhance.Sharpness(main_img_adjusted).enhance(self.sharpness)

        self.temp_image = Image.blend(main_img_adjusted, collage_background,self.alpha)

        self.update_preview(self.temp_image)

            

root = tk.Tk()
app = Application(master=root)
app.mainloop()

#if __name__ == "__main__":
#    main()

