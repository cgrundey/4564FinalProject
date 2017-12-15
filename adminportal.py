from tkinter import *
import requests
import sys

serverip = sys.argv[1] #ip of authenticationpi is command line arg

###############################ADD######################################

def add_tag_user():
	print("ADD:  User ID: %s\nTag ID: %s" % (e1.get(), e2.get()))
	r = requests.post('http://{}:5000/add_tag_user'.format(serverip), json = {'user' : e1.get(), 'tag': e2.get()}, auth=('Apple', 'Pie'))
	print (r.status_code)

def add_locker_user():
	print("ADD:  User ID: %s\nLocker ID: %s" % (e3.get(), e4.get()))
	r = requests.post('http://{}:5000/add_locker_user'.format(serverip), json = {'user' : e3.get(), 'locker' : e4.get()}, auth=('Apple', 'Pie'))
	print (r.status_code)
	
	
#############################REMOVE#####################################

def remove_tag_user():
	print("REMOVE:  User ID: %s\nTag ID: %s" % (e1.get(), e2.get()))
	r = requests.delete('http://{}:5000/remove_tag_user'.format(serverip), json = {'user' : e1.get(), 'tag': e2.get()}, auth=('Apple', 'Pie'))
	print (r.status_code)
	
def remove_locker_user():
	print("REMOVE:  User ID: %s\nLocker ID: %s" % (e3.get(), e4.get()))
	r = requests.delete('http://{}:5000/remove_locker_user'.format(serverip), json = {'user' : e3.get(), 'locker': e4.get()}, auth=('Apple', 'Pie'))
	print (r.status_code)
	
	
#############################TKINTER####################################

def enter():
	if v.get() == 1:
		add_tag_user()
	elif v.get() == 2:
		add_locker_user()
	elif v.get() == 3:
		remove_tag_user()
	elif v.get() == 4:
		remove_locker_user()

def radio_changed():
	if v.get() == 1 or v.get() == 3:
		e1.config(state=NORMAL)
		e2.config(state=NORMAL)
		e3.config(state=DISABLED)
		e4.config(state=DISABLED)
	if v.get() == 2 or v.get() == 4:
		e1.config(state=DISABLED)
		e2.config(state=DISABLED)
		e3.config(state=NORMAL)
		e4.config(state=NORMAL)
	
root = Tk()
root.title("Admin Portal")
v = IntVar()

Label(root, text="User ID").grid(row=0)
Label(root, text="Tag ID").grid(row=1)
Label(root, text="User ID").grid(row=2)
Label(root, text="Locker ID").grid(row=3)

e1 = Entry(root)
e2 = Entry(root)
e3 = Entry(root, state=DISABLED)
e4 = Entry(root, state=DISABLED)
e1.grid(row=0, column=1)
e2.grid(row=1, column=1)
e3.grid(row=2, column=1)
e4.grid(row=3, column=1)

Button(root, text='Quit', command=root.quit).grid(row=4, column=0, sticky=W, pady=4)
Button(root, text='Enter', command=enter).grid(row=4, column=1, sticky=W, pady=4)
 
rad1 = Radiobutton(root, text="Add Tag to User", variable=v, value=1, command=radio_changed)
rad1.grid(row=0, column=2, sticky=W, padx=30)
rad1.select()
rad2 = Radiobutton(root, text="Add User To Locker", variable=v, value=2, command=radio_changed)
rad2.grid(row=1, column=2, sticky=W, padx=30)
rad3 = Radiobutton(root, text="Remove Tag From User", variable=v, value=3, command=radio_changed)
rad3.grid(row=2, column=2, sticky=W, padx=30)
rad4 = Radiobutton(root, text="Remove User From Locker", variable=v, value=4, command=radio_changed)
rad4.grid(row=3, column=2, sticky=W, padx=30)

mainloop()
