import pandas as pd
import sys
import pathlib as pl
import tkinter as tk
import matplotlib as mpl
from tkinter import filedialog
from tkinter.ttk import Treeview
from tkinter import ttk
from tkinter import messagebox as mbox

background_color_main='#262624'
text_color="#E9E9E9"
button_backg_color="#30302E"

class CycloMeter():
    def __init__(self, path):
        self.pathAssign(path)
        self.msToKM('average speed')
        self.msToKM('max speed')
        self.secsToHour('moving time')
        self.condition=None

    def pathAssign(self, path: str):
        path = pl.Path(path)
        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise IOError(f"Failed to read CSV: {e}") from e
        df.columns = [c.lower() for c in df.columns]
        self.data = df.copy()   # keep copy
        return self
    
    def setCondition(self, condition):
        if condition is None:
            self.condition=None
        else:
            self.condition=condition
    
    def filterResults(self, column: str, operator: str, value: float):
        if value=='':
            condition=None
            self.setCondition(condition)
            print('Filter is removed, insert table for default view.')
            pass
        elif operator == ">":
            value=int(value)
            condition=self.data[column]>value
            self.setCondition(condition)
            print('Filterization is complete!')
        elif operator == "<":
            value=int(value)
            condition=self.data[column]<value
            self.setCondition(condition)
            print('Filterization is complete!')
        else:
            print('Invalid operator. (< or >)')
            return False
    
    def extractColumn(self, column:str):
        '''return column
        mutates self.data obj'''
        column=column.lower()
        if column in self.data.columns:
            return self.data[f"{column}"]
        else:
            raise KeyError("Column not found.")

    def extractMultiColumns(self, column:list):
        """Takes list with items as column str"""

        return self.data[column]

    def msToKM(self, column:str):
        col = column.lower()
        if col not in self.data.columns:
            raise KeyError(col)
        self.data = self.data.assign(**{f"{col} kmh": (self.data[col].astype(float) * 3.6).round(2)})

    def secsToHour(self, column):
        '''convert speed format to kmh'''
        if column in self.data.columns:
            meter=self.extractColumn(column)
            meter=meter/3600
            meter=round(meter, 3)
            self.data[f"{column}/h"]=meter

class TextRedirector():
    def __init__(self, text_widget, delay=50):
        self.text_widget = text_widget
        self.delay = delay
        self.text = ""
        self.index = 0

    def write(self,text):
        if self.index == 0:
            self.text_widget.configure(state='normal')
            self.text_widget.delete("1.0", "end")
            self.text_widget.configure(state='disabled')
            self.text = text
            self.insert_next_char()

    def insert_next_char(self):
        if self.index < len(self.text):
            char = self.text[self.index]
            self.text_widget.configure(state='normal')
            self.text_widget.insert("end", char)
            self.text_widget.see("end")
            self.text_widget.configure(state='disabled')

            self.index += 1
            self.text_widget.after(self.delay, self.insert_next_char)
        else:
            self.index = 0

    def flush(self):
        pass

def loadFile():
    global cyclingObj
    items=['activity id', 'activity date', 'moving time/h', 'distance', 'max heart rate', 'average heart rate', 'average speed kmh', 'max speed kmh', 'average watts', 'calories'] 
    
    path=filedialog.askopenfilename()
    if path:
        cyclingObj=CycloMeter(path)
        cyclingObj.data=cyclingObj.data[items]
    else:
        pass

def displayData(cyclingObj:CycloMeter):
    
    if cyclingObj.condition is not None: #If data is filtered, adjust the view.
        display_data=cyclingObj.data[cyclingObj.condition]
    else: #Unfiltered, raw data copy.
        display_data=cyclingObj.data #iterate dataframe records and get Series
    return display_data

def updateStatusBar(status_bar:tk.Text):
    sys.stdout=TextRedirector(status_bar)
    

def treeview_init(tree_view:Treeview, display_data, pandasRows):
    '''Adjust, insert and clear treeview'''
    for t in tree_view.get_children(): tree_view.delete(t)
    for i in list(display_data.columns): 

        tree_view.heading(i, text=i) #headings
        tree_view.column(i, width=180) #column sorting
    
    for index, value in pandasRows: #Iterating through pandasRows
        raw_values=value.values #Series obj (bool T/F) to raw values
        tree_view.insert('','end',values=raw_values.tolist()) #''(start) to end insertion of columns not records
    print(f"Table insertion is complete!") #debugging needs removed on scaffolding


def insertTable():

    display_data=displayData(cyclingObj)
    tree_view['columns']=list(display_data.columns) #update tree_view obj
    tree_view.column('#0', width=0, stretch=False)
    pandasRows=display_data.iterrows() #iterate dataframe records and get Series
    treeview_init(tree_view, display_data, pandasRows)

def retrieveEntry(colmn,op,setVal):
    '''Return input of textBox'''
    colmn=colmn.get()
    operator=op.get()
    val=setVal.get()
    cyclingObj.filterResults(colmn,operator,val)

def initButtons(window):
    global colmn,op,setVal,frame_1,frame_2,frame_3, frame_4
    for i in range(4):
        if i==0:
            frame_1=tk.Frame(window)
            colmn=tk.Entry(frame_1)
            
        elif i==1:
            frame_2=tk.Frame(window)
            op=tk.Entry(frame_2)
            
        elif i==2:
            frame_3=tk.Frame(window)
            setVal=tk.Entry(frame_3)
        elif i==3:
            frame_4=tk.Frame(window)
            

def packButtons(colmn,op,setVal,frame_1,frame_2,frame_3):
    
    
    for index, value in enumerate(["Column:", "Operation:", "Set Value:"]):
        
        if index==0:
            colmLabel=tk.Label(frame_1, text='column:')
            frame_1.pack(side='top')
            colmn.pack(side=tk.RIGHT)
            colmLabel.pack(side=tk.LEFT)
            
        elif index==1:
            operatorLabel=tk.Label(frame_2, text='operator:')
            frame_2.pack(side='top')
            op.pack(side=tk.RIGHT)
            operatorLabel.pack(side=tk.LEFT)
            
        elif index==2:
            valueLabel=tk.Label(frame_3, text='value:')
            frame_3.pack(side='top')
            setVal.pack(side=tk.RIGHT)
            valueLabel.pack(side=tk.LEFT)
    status_bar=tk.Text(frame_4, state='disabled')
    frame_4.pack(side='right', fill="x")
    status_bar.pack(fill="x") 
    updateStatusBar(status_bar) 

def applyStyle(window:tk.Tk, style:ttk.Style):
    window.option_add('*Button.background', button_backg_color)
    window.option_add('*Button.foreground', text_color)
    window.option_add('*Text.background', button_backg_color)
    window.option_add('*Text.foreground', text_color)
    window.option_add('*Text.font', ('Segoe UI', 12))
    window.option_add('*Label.background', button_backg_color)
    window.option_add('*Label.foreground', text_color)
    window.option_add('*Entry.background', button_backg_color)
    window.option_add('*Entry.foreground', text_color)
    style.theme_use('clam')
    style.configure("Treeview", background='#262624', foreground='#E9E9E9', fieldbackground='#262624',font=('Segoe UI', 12))
    style.configure("Treeview.Heading", background='#262624', foreground='#E9E9E9', fieldbackground='#262624')
    style.map("Treeview",
    foreground=[('pressed', '#E9E9E9'), ('active', '#E9E9E9')],
    background=[('selected', "#6791C1"),('pressed', '!disabled', "#6791C1"), ('active', '#262624')]
    )
    style.map("Treeview.Heading",
    foreground=[('pressed', '#E9E9E9'), ('active', '#E9E9E9')],
    background=[('pressed', '!disabled', "#6791C1"), ('active', '#262624')]
    )

def programInitialize():
    global tree_view
    window=tk.Tk(className="cycloMeter")
    window.configure(background=background_color_main)
    window.geometry('1200x800')
    style=ttk.Style(master=window)
    applyStyle(window,style)

    buttonLoadFile=tk.Button(window, text='Load CSV File', command=loadFile)
    buttonInsertTable=tk.Button(window, text="Insert Table", command=insertTable)
    initButtons(window)

    buttonFilter=tk.Button(window, text='Filter', command=lambda:retrieveEntry(colmn,op,setVal)) #text box
    tree_view=Treeview(window, height=26) #CHANGE
    
    for i in [tree_view,buttonLoadFile,buttonFilter,buttonInsertTable]: i.pack()
    packButtons(colmn,op,setVal,frame_1,frame_2,frame_3)
    

    window.mainloop()

if __name__ == "__main__":
    programInitialize()
    
    """
    STATUS: 
        Loading columns, data works
        Filtering works
        Interface is a bit better
        .exe file is init_ed

    
    TODO:
        Display success or failure of filter on GUI
    
    """