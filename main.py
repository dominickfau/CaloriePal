from tkinter import *
from tkinter import ttk
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import filedialog
import json
from caloriePal import CaloriePal, ServingUom, Food


class GUI:
    VERSION = "0.0.1"
    PROGRAM_NAME = "Calorie Pal"
    FLOAT_START = 0.0
    START = 0

    def __init__(self, parentWindow, calPal):
        self.mainWindow = parentWindow
        self.calPal = calPal
        self.barcodeValue = ""

        self.font = ("TkDefaultFont", 16, "normal")

        self.mainWindowHeight = 75
        self.mainWindowWidth = 480

        self.foodWindowHeight = 400
        self.foodWindowWidth = 675

        self.settingsWindowHeight = 210
        self.settingsWindowWidth = 400

        self.uomWindowHeight = 100
        self.uomWindowWidth = 475

        self.helpWindowHeight = 100
        self.helpWindowWidth = 475

        self.rawFoodDataWindowHeight = 550
        self.rawFoodDataWindowWidth = 600

        self.mainWindow.title(self.PROGRAM_NAME)
        self.mainWindow.geometry(f"{self.mainWindowWidth}x{self.mainWindowHeight}")
        self.mainWindow.minsize(self.mainWindowWidth, self.mainWindowHeight)

        self.mainWindow.protocol("WM_DELETE_WINDOW", self.cleanExit)
        self.mainWindow.bind("<Return>", self.onMainWindowEvent)
        self.mainWindow.bind("<Tab>", self.onMainWindowEvent)

        self._populateMainWindow()

        # For testing.
        self.mainWindowBarcodeEntry.insert(END, "041271025903")
        self.mainWindowFindButton.invoke()

    def cleanExit(self):
        self.calPal.saveFoodDataFile()
        self.calPal.saveSettingsFile()
        exit()
    
    def _populateMainWindow(self):
        self.rootMenubar = Menu(self.mainWindow)
        self.mainWindow.config(menu=self.rootMenubar)

        self.rootFilemenu = Menu(self.rootMenubar, tearoff=False)
        self.rootDatamenu = Menu(self.rootMenubar, tearoff=False)

        self.rootMenubar.add_cascade(label="File", menu=self.rootFilemenu)
        self.rootMenubar.add_cascade(label="Data", menu=self.rootDatamenu)

        self.rootFilemenu.add_command(label="Settings", command=self.openSettingsWindow)
        self.rootFilemenu.add_command(label="Help", command=self.openHelpWindow)
        self.rootFilemenu.add_command(label="Exit", command=self.cleanExit)

        self.rootDatamenu.add_command(label="Change Food Data File", command=self.changeFoodDataFile)
        self.rootDatamenu.add_command(label="View Raw Food Data", command=self.openViewRawFoodDataWindow)



        self.mainWindowBarcodeLabel = Label(self.mainWindow, text="Barcode:", font=self.font)
        self.mainWindowBarcodeLabel.grid(row=0, column=0)

        self.mainWindowBarcodeEntry = Entry(self.mainWindow, font=self.font, width=35)
        self.mainWindowBarcodeEntry.grid(row=0, column=1, pady=3)

        self.mainWindowFindButton = Button(self.mainWindow, text="Find", command=self.findFoodByBarcode, font=self.font)
        self.mainWindowFindButton.grid(row=10, column=0, columnspan=2, pady=3)

        self.mainWindowBarcodeEntry.focus()
    
    def resetMainWindow(self):
        self.mainWindowBarcodeEntry.delete(GUI.START, END)
    

    def findFoodByBarcode(self):
        self.barcodeValue = self.mainWindowBarcodeEntry.get().strip()
        if len(self.barcodeValue) <= 0:
            messagebox.showerror(self.PROGRAM_NAME, "Please scan or enter a barcode to lookup.",parent=self.mainWindow)
            self.mainWindowBarcodeEntry.focus()
            return
        
        data = self.calPal.findFoodDataByBarcode(self.barcodeValue)

        if data:
            self.openUpdateFoodWindow()
            self.resetMainWindow()
            return

        else:
            messagebox.showinfo(self.PROGRAM_NAME, "Could not find item matching that barcode.", parent=self.mainWindow)
            self.resetMainWindow()
            self.openAddFoodWindow()
            return

    def onMainWindowEvent(self, event=None):
        self.findFoodByBarcode()

    def openSettingsWindow(self):
        self.settingsWindow = Toplevel(self.mainWindow)
        self.settingsWindow.title("Edit Settings")
        self.settingsWindow.bind("<Return>", self.cleanExit)

        self.settingsWindow.geometry(f"{self.settingsWindowWidth}x{self.settingsWindowHeight}")
        self.settingsWindow.minsize(self.settingsWindowHeight, self.settingsWindowWidth)

    def changeFoodDataFile(self):
        response = False
        msg = "You are about to change the active food data file. Any unsaved changes will be lost unless you close and reopen the program.\n\nDo you want to proceed with changing the data file?"

        response = messagebox.askyesno(self.mainWindow.title(), msg, parent=self.mainWindow)

        if response:
            filePath = filedialog.askopenfilename(filetypes =[('Food Data Files', '*.json')])
            changeOk, msg = self.calPal.changeFoodDataFile(filePath)

            if changeOk == False:
                msg = f"An error ocurred when changing data file. Reverting back to original data file.\n\nError: {msg}"
                messagebox.showwarning(self.mainWindow.title(), msg, parent=self.mainWindow)
            else:
                messagebox.showinfo(self.mainWindow.title(), msg, parent=self.mainWindow)

        return

    def openViewRawFoodDataWindow(self):
        self.rawFoodDataWindow = Toplevel(self.mainWindow)
        self.rawFoodDataWindow.title("Raw Food Data Viewer")

        self.rawFoodDataWindow.geometry(f"{self.rawFoodDataWindowWidth}x{self.rawFoodDataWindowHeight}")
        self.rawFoodDataWindow.minsize(self.rawFoodDataWindowWidth, self.rawFoodDataWindowHeight)

        self.rawFoodDataLabel = Label(self.rawFoodDataWindow, text="", font=self.font)
        self.rawFoodDataLabel.pack(fill='x')

        self.rawFoodDataText = Text(self.rawFoodDataWindow, relief=SUNKEN, borderwidth=1, font=self.font)
        self.rawFoodDataText.pack(expand=True, fill='both')
        self.rawFoodDataText.bind("<KeyRelease>", self.onRawFoodDataTextEvent)

        self.insertRawFoodData()

        self.rawFoodDataSaveButton = Button(self.rawFoodDataWindow, text="Save", font=self.font, command=self.saveFoodDataFromRaw)
        self.rawFoodDataSaveButton.pack(ipadx=10, ipady=5)

    def onRawFoodDataTextEvent(self, event=None):
        self.rawFoodDataLabel.config(text="Unsaved Changes Exists")

    def insertRawFoodData(self):
        self.rawFoodDataText.delete(GUI.FLOAT_START, END)

        data = {}
        data = self.calPal.getFoodDataJson()
        dataString = json.dumps(data, indent=4)

        self.rawFoodDataText.insert(GUI.FLOAT_START, dataString)

    def saveFoodDataFromRaw(self):
        self.rawFoodDataLabel.config(text="File Saved")





    def openAddFoodWindow(self):
        self.addNewFoodWindow = Toplevel(self.mainWindow)
        self.addNewFoodWindow.title("Add New Food Item")
        self.addNewFoodWindow.bind("<Return>", self.addFood)

        self.addNewFoodWindow.geometry(f"{self.foodWindowWidth}x{self.foodWindowHeight}")
        self.addNewFoodWindow.minsize(self.foodWindowWidth, self.foodWindowHeight)

        self._populateFoodWindow(self.addNewFoodWindow)

        self.addNewFoodSaveFoodButton = Button(self.addNewFoodWindow, text="Save Food", command=self.addFood, font=self.font)
        self.addNewFoodSaveFoodButton.grid(row=100, column=0, columnspan=6, pady=3)

    def openUpdateFoodWindow(self):
        self.updateFoodWindow = Toplevel(self.mainWindow)
        self.updateFoodWindow.title("Update Food Item")
        self.updateFoodWindow.bind("<Return>", self.updateFood)

        self.updateFoodWindow.geometry(f"{self.foodWindowWidth}x{self.foodWindowHeight}")
        self.updateFoodWindow.minsize(self.foodWindowWidth, self.foodWindowHeight)

        self._populateFoodWindow(self.updateFoodWindow, insertValues=True)

        self.updateFoodSaveFoodButton = Button(self.updateFoodWindow, text="Save Food", command=self.updateFood, font=self.font)
        self.updateFoodSaveFoodButton.grid(row=100, column=0, columnspan=6, pady=3)
    

    def _populateFoodWindow(self, parentWindow, insertValues=False):
        self.barcodeLabel = Label(parentWindow, text="Barcode:", font=self.font)
        self.barcodeLabel.grid(row=0, column=0, sticky="E")

        self.barcodeEntry = Entry(parentWindow, font=self.font, width=35)
        self.barcodeEntry.grid(row=0, column=1, pady=1, columnspan=3)
        self.barcodeEntry.delete(GUI.START, END)
        self.barcodeEntry.insert(END, self.barcodeValue)

        self.foodDescriptionLabel = Label(parentWindow, text="Description:", font=self.font)
        self.foodDescriptionLabel.grid(row=1, column=0, sticky="E")

        self.foodDescriptionEntry = Entry(parentWindow, font=self.font, width=35)
        self.foodDescriptionEntry.grid(row=1, column=1, pady=1, columnspan=3)
        if insertValues:
            self.foodDescriptionEntry.delete(GUI.START, END)
            self.foodDescriptionEntry.insert(END, self.calPal.foodData[self.barcodeValue].description)

        self.foodDetailedDescriptionLabel = Label(parentWindow, text="Detailed Description:", font=self.font)
        self.foodDetailedDescriptionLabel.grid(row=2, column=0, sticky="E")

        self.foodDetailedDescriptionEntry = Text(parentWindow, width=35, height=5, relief=SUNKEN, borderwidth=1, font=self.font)
        self.foodDetailedDescriptionEntry.grid(row=2, column=1, pady=1, columnspan=3)
        if insertValues:
            self.foodDetailedDescriptionEntry.delete(GUI.FLOAT_START, END)
            self.foodDetailedDescriptionEntry.insert(END, self.calPal.foodData[self.barcodeValue].detailedDescription)

        self.foodCaloriesPerServingLabel = Label(parentWindow, text="Calories Per Serving:", font=self.font)
        self.foodCaloriesPerServingLabel.grid(row=3, column=0, sticky="E")

        self.foodCaloriesPerServingEntry = Entry(parentWindow, font=self.font, width=35)
        self.foodCaloriesPerServingEntry.grid(row=3, column=1, pady=1, columnspan=3)
        if insertValues:
            self.foodCaloriesPerServingEntry.delete(GUI.START, END)
            self.foodCaloriesPerServingEntry.insert(END, self.calPal.foodData[self.barcodeValue].caloriesPerServing)

        self.foodServingSizeLabel = Label(parentWindow, text="Serving Size:", font=self.font)
        self.foodServingSizeLabel.grid(row=4, column=0, sticky="E")

        self.foodServingSizeEntry = Entry(parentWindow, font=self.font, width=35)
        self.foodServingSizeEntry.grid(row=4, column=1, pady=1, columnspan=3)
        if insertValues:
            self.foodServingSizeEntry.delete(GUI.START, END)
            self.foodServingSizeEntry.insert(END, self.calPal.foodData[self.barcodeValue].servingSize)

        self.foodServingSizeUomLabel = Label(parentWindow, text="Serving Size UOM:", font=self.font)
        self.foodServingSizeUomLabel.grid(row=5, column=0, sticky="E")

        self.foodServingSizeUomValue = tk.StringVar()
        self.foodServingSizeUomCombobox = ttk.Combobox(parentWindow, textvariable=self.foodServingSizeUomValue, font=self.font)
        self.foodServingSizeUomCombobox.grid(row=5, column=1, pady=1)

        self.foodServingSizeUomAddButton = Button(parentWindow, text="Add", command=self.openAddUomWindow, font=self.font)
        self.foodServingSizeUomAddButton.grid(row=5, column=2, pady=3)

        self.foodServingSizeUomUpdateButton = Button(parentWindow, text="Update", command=self.openAddUomWindow, font=self.font)
        self.foodServingSizeUomUpdateButton.grid(row=5, column=3, pady=3)

        self.updateFoodServingUomCombobox()

        if insertValues:
            uomName = self.calPal.foodData[self.barcodeValue].servingSizeUom.name

            for x, uom in enumerate(self.calPal.servingUoms):
                if uomName == uom.name:
                    self.foodServingSizeUomCombobox.current(x)

        self.foodDescriptionEntry.focus()

    def updateFoodServingUomCombobox(self, index=0):
        """Updates serving UOM combobox.

        Args:
            index (int, optional): Used to set selected item in the combobox by item index. Defaults to 0.
        """
        values = []
        for uom in self.calPal.servingUoms:
            values.append(uom.name)

        self.foodServingSizeUomCombobox['values'] = tuple(values)
        self.foodServingSizeUomCombobox.current(index)

    def validateFoodWindow(self):
        formValid = True

        if len(self.barcodeEntry.get().strip()) <= 0: formValid = False
        if len(self.foodDescriptionEntry.get().strip()) <= 0: formValid = False
        if len(self.foodDetailedDescriptionEntry.get(GUI.FLOAT_START, END).strip()) <= 0: formValid = False
        if len(self.foodCaloriesPerServingEntry.get().strip()) <= 0: formValid = False
        if len(self.foodServingSizeEntry.get().strip()) <= 0: formValid = False

        return formValid

    def addFood(self, event=None):
        if not self.validateFoodWindow():
            messagebox.showerror(self.addNewFoodWindow.title(), "All fields are required.", parent=self.addNewFoodWindow)
            return

        #TODO: Write a more detailed error msg.
        uomName = self.foodServingSizeUomValue.get()
        if uomName == None or len(uomName) <= 0:
            err = "Serving UOM combobox returned a value of 'None'."
            messagebox.showerror(self.addNewFoodWindow.title(), f"An internal error ocurred. Item will not be added. Error: {err}",
                                    parent=self.addNewFoodWindow)
            return

        selectedUom = self.calPal.findUomByName(uomName)
        if selectedUom == None:
            err = f"findUomByName('{uomName}') returned 'None'."
            messagebox.showerror(self.addNewFoodWindow.title(), f"An internal error ocurred. Item will not be added. Error: {err}",
                                    parent=self.addNewFoodWindow)
            return

        food = Food(self.barcodeEntry.get().strip(),
                    self.foodDescriptionEntry.get().strip(),
                    self.foodDetailedDescriptionEntry.get(GUI.FLOAT_START, END).strip(),
                    self.foodCaloriesPerServingEntry.get().strip(),
                    self.foodServingSizeEntry.get().strip(),
                    selectedUom)
        
        try:
            self.calPal.addFood(food)
        except Exception as err:
            messagebox.showerror(self.addNewFoodWindow.title(), f"Could not add item to database.\n\nError: {err}", parent=self.addNewFoodWindow)
            return

        messagebox.showinfo(self.addNewFoodWindow.title(), "Item added.", parent=self.addNewFoodWindow)
        self.addNewFoodWindow.destroy()
        return
    
    def updateFood(self, event=None):
        #TODO: Code updateFood().
        messagebox.showinfo(self.updateFoodWindow.title(), "Item updated.", parent=self.updateFoodWindow)
        self.updateFoodWindow.destroy()
        return

    def openAddUomWindow(self):
        self.addUomWindow = Toplevel(self.mainWindow)
        self.addUomWindow.title("Add UOM")
        self.addUomWindow.bind("<Return>", self.addUom)

        self.addUomWindow.geometry(f"{self.uomWindowWidth}x{self.uomWindowHeight}")
        self.addUomWindow.minsize(self.uomWindowWidth, self.uomWindowHeight)

        self._populateUomWindow(self.addUomWindow)

        self.addUomSaveButton = Button(self.addUomWindow, text="Save UOM", command=self.addUom, font=self.font)
        self.addUomSaveButton.grid(row=100, column=0, columnspan=3, pady=3)
    
    def openUpdateUomWindow(self, index):
        self.updateUomWindow = Toplevel(self.mainWindow)
        self.updateUomWindow.title("Update UOM")
        self.updateUomWindow.bind("<Return>", self.updateUom)

        self.updateUomWindow.geometry(f"{self.uomWindowWidth}x{self.uomWindowHeight}")
        self.updateUomWindow.minsize(self.uomWindowWidth, self.uomWindowHeight)

        self._populateUomWindow(self.updateUomWindow, index, insertValues=True)

        self.updateUomSaveButton = Button(self.updateUomWindow, text="Save UOM", command=self.updateUom, font=self.font)
        self.updateUomSaveButton.grid(row=100, column=0, columnspan=3, pady=3)
    
    def _populateUomWindow(self, parentWindow, index=0, insertValues=False):
        self.uomWindowNameLabel = Label(parentWindow, text="Name:", font=self.font)
        self.uomWindowNameLabel.grid(row=0, column=0, sticky="E")

        self.uomWindowNameEntry = Entry(parentWindow, font=self.font, width=35)
        self.uomWindowNameEntry.grid(row=0, column=1)
        if insertValues:
            self.uomWindowNameEntry.delete(GUI.START, END)
            self.uomWindowNameEntry.insert(END, self.calPal.servingUoms[index].name)

        self.uomWindowCodeLabel = Label(parentWindow, text="Code:", font=self.font)
        self.uomWindowCodeLabel.grid(row=1, column=0, sticky="E")

        self.uomWindowCodeEntry = Entry(parentWindow, font=self.font, width=35)
        self.uomWindowCodeEntry.grid(row=1, column=1)
        if insertValues:
            self.uomWindowCodeEntry.delete(GUI.START, END)
            self.uomWindowCodeEntry.insert(END, self.calPal.servingUoms[index].code)

        self.uomWindowNameEntry.focus()
    
    def validateUomWindow(self):
        formValid = True

        if len(self.uomWindowNameEntry.get().strip()) <= 0 : formValid = False
        if len(self.uomWindowCodeEntry.get().strip()) <= 0 : formValid = False

        return formValid

    def addUom(self, event=None):
        if not self.validateUomWindow():
            messagebox.showerror(self.addUomWindow.title(), "All fields are required.", parent=self.addUomWindow)
            return
        
        uomName = self.uomWindowNameEntry.get().strip()
        uomCode = self.uomWindowCodeEntry.get().strip()

        for uom in self.calPal.servingUoms:
            if uomName == uom.name or uomCode == uom.code:
                messagebox.showerror(self.addUomWindow.title(), "A UOM with this name and or code already exists.", parent=self.addUomWindow)
                return
        
        uom = ServingUom(uomName, uomCode)

        self.calPal.addUom(uom)
        self.updateFoodServingUomCombobox(index = len(self.calPal.servingUoms) - 1)
        # messagebox.showinfo(self.addUomWindow.title(), "UOM added.", parent=self.addUomWindow)
        self.addUomWindow.destroy()
        return
    
    def updateUom(self, event=None):
        #TODO: Code updateUom().
        if not self.validateUomWindow():
            messagebox.showerror(self.updateUomWindow.title(), "All fields are required.", parent=self.updateUomWindow)
            return

    def openHelpWindow(self):
        self.helpWindow = Toplevel(self.mainWindow)
        self.helpWindow.title("Help")
        self.helpWindow.bind("<Return>", self.cleanExit)

        self.helpWindow.geometry(f"{self.helpWindowWidth}x{self.helpWindowHeight}")
        self.helpWindow.minsize(self.helpWindowWidth, self.helpWindowHeight)

        self.versionLabel = Label(self.helpWindow, text=f"Program Version: {GUI.VERSION}", font=self.font)
        self.versionLabel.grid(row=0, column=0)







if __name__ == "__main__":
    root = Tk()
    calPal = CaloriePal()
    app = GUI(root, calPal)
    root.mainloop()