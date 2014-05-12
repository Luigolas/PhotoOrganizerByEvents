__author__ = 'luigolas'

import Tkinter as tk
from PIL import Image, ImageTk
import PhotoEventOrganizer

root = tk.Tk()
root.title("display an image")
image = Image.open("/home/luigolas/PycharmProjects/PyPhoto/TestPhotos/CAM00019.jpg")
photo = ImageTk.PhotoImage(image)
cv = tk.Canvas()
cv.pack(side='top', fill='both', expand='yes')
cv.create_image(10, 10, image=photo, anchor='nw')
root.mainloop()
