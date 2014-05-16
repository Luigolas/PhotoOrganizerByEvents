__author__ = 'luigolas'

import Tkinter as tk
from PIL import Image, ImageTk
# import PhotoEventOrganizer


#quit
def quit(root):
    root.quit()
    root.destroy()


def show_pics(pics):
    root = tk.Tk()
    root.title("Loose photos?")
    w, h, x, y = 300, 600, 0, 0
    root.geometry("%dx%d+%d+%d" % (w, h, x, y))
    labels = []
    for pic in pics:
        image = Image.open(pic)
        image = image.resize((200, 200), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=photo)
        label.pack()
        label.img = photo
        labels.append(label)
        # cv = tk.Canvas()
        # cv.pack(side='top', fill='both', expand='yes')
        # cv.create_image(10, 10, image=photo, anchor='nw')

    root.mainloop()
