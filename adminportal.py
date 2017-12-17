from tkinter import *
import requests
import sys

serverip = sys.argv[1] #ip of authenticationpi is command line arg

###############################ADD######################################

def add_tag_locker():
	print("ADD:  Locker: %s\nTag ID: %s" % (e1.get(), e2.get()))
	r = requests.post('http://{}:5000/add_tag_user'.format(serverip), json = {'user' : e1.get(), 'tag': e2.get()}, auth=('Apple', 'Pie'))
	print (r.status_code)
	
#############################REMOVE#####################################

def remove_tag_locker():
	print("REMOVE:  User ID: %s\nTag ID: %s" % (e1.get(), e2.get()))
	r = requests.delete('http://{}:5000/remove_tag_user'.format(serverip), json = {'user' : e1.get(), 'tag': e2.get()}, auth=('Apple', 'Pie'))
	print (r.status_code)
	
	
#############################TKINTER####################################

def enter():
	if v.get() == 1:
		add_tag_locker()
	elif v.get() == 2:
		remove_tag_locker()
	
root = Tk()
root.title("Admin Portal")
v = IntVar()

Label(root, text="Locker ID").grid(row=0)
Label(root, text="Tag ID").grid(row=1)

e1 = Entry(root).grid(row=0, column=1)
e2 = Entry(root).grid(row=1, column=1)

Button(root, text='Quit', command=root.quit).grid(row=2, column=0, sticky=W, pady=4)
Button(root, text='Enter', command=enter).grid(row=2, column=1, sticky=W, pady=4)
 
rad1 = Radiobutton(root, text="Add Tag to Locker", variable=v, value=1)
rad1.grid(row=0, column=2, sticky=W, padx=30)
rad1.select()
rad2 = Radiobutton(root, text="Remove Tag From Locker", variable=v, value=2)
rad2.grid(row=1, column=2, sticky=W, padx=30)

mainloop()
