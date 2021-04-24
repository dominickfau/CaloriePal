import json
import os
import os.path

class ServingUom(object):
    REQUIRED_KEYS = ["name", "code"]

    def __init__(self, name, code):
        self.name = name
        self.code = code

    @classmethod
    def fromDictionary(cls, data):
        """Creates a new ServingUom object from a dictionary.

        Args:
            data (dict): Dictionary containing a 'name' and 'code' key value pair.

        Raises:
            TypeError: Raised if object provided is not of type dict().
            KeyError: Raised if a required key is missing.

        Returns:
            ServingUom Object: Returns a new ServingUom object.
        """
        if not isinstance(data, dict):
            raise TypeError("data must be of type dict().")
        
        for requiredKey in cls.REQUIRED_KEYS:
            if requiredKey not in data.keys():
                raise KeyError(f"Missing required key '{requiredKey}'")

        name = data['name']
        code = data['code']

        return ServingUom(name, code)
    
    @classmethod
    def fromDictionaryList(cls, dataList):
        """Creates a list of new ServingUom objects from a dictionary list.

        Args:
            dataList (list): List of dictionaries containing a 'name' and 'code' key value pair.

        Raises:
            TypeError: Raised if object provided is not of type list().
            ValueError: Raised if list is empty.

        Returns:
            list: Returns a list of ServingUom objects.
        """
        toReturn = []

        if not isinstance(dataList, list): raise TypeError("dataList must be of type list().")

        #TODO: Check if this is thr right  error type for this.
        if len(dataList) <= 0: raise ValueError("List must contain items.")
        
        for item in dataList:
            toReturn.append(cls.fromDictionary(item))
        
        return toReturn

    @staticmethod
    def toDict(servingUom):
        """Converts ServingUom object attributes into key: value pairs.

        Args:
            servingUom (ServingUom Object): ServingUom object to convert.

        Returns:
            dict: ServingUom object attributes as key: value pairs.
        """
        objData = {}
        if not isinstance(servingUom, ServingUom): raise TypeError("food must be of type ServingUom().")

        for item in vars(servingUom):
            objData[item] = getattr(servingUom, item)
        return objData



class Food(object):
    REQUIRED_KEYS = ["barcode", "description", "detailedDescription", "caloriesPerServing", "servingSize", "servingSizeUom"]

    def __init__(self, barcode, description, detailedDescription, caloriesPerServing, servingSize, servingSizeUom):
        """Creates a new Food object.

        Args:
            barcode (string): Unique product barcode. Used to identify each product.
            description (string): Description to use for this food.
            detailedDescription (string): Detailed Description of this food.
            caloriesPerServing (float): Number of calories per serving.
            servingSize (float): Weight per serving size. Weight UOM set with servingSizeUom.
            servingSizeUom (ServingUom object, optional): Serving size UOM object for this food.
        """
        if not isinstance(servingSizeUom, ServingUom): raise TypeError("servingSizeUom must be of type ServingUom().")
        
        self.barcode = barcode
        self.description = description
        self.detailedDescription = detailedDescription
        self.caloriesPerServing = caloriesPerServing
        self.servingSize = servingSize
        self.servingSizeUom = servingSizeUom

    @classmethod
    def fromDictionary(cls, data):
        """Creates a new Food object from a dictionary.

        Args:
            data (dict): Dictionary containing all required key value pairs.

        Raises:
            TypeError: Raised if object provided is not of type dict().
            KeyError: Raised if a required key is missing.

        Returns:
            Food Object: Returns a new Food object.
        """
        if not isinstance(data, dict):
            raise TypeError("data must be of type dict().")
        
        for requiredKey in cls.REQUIRED_KEYS:
            if requiredKey not in data.keys():
                raise KeyError(f"Missing required key '{requiredKey}'")

        barcode = data['barcode']
        description = data['description']
        detailedDescription = data['detailedDescription']
        caloriesPerServing = data['caloriesPerServing']
        servingSize = data['servingSize']
        servingSizeUom = ServingUom.fromDictionary(data['servingSizeUom'])

        return Food(barcode, description, detailedDescription, caloriesPerServing, servingSize, servingSizeUom)
    
    @classmethod
    def fromDictionaryList(cls, dataList):
        """Creates a list of new Food objects from a dictionary list.

        Args:
            dataList (list): List of dictionaries containing all required key value pairs.

        Raises:
            TypeError: Raised if object provided is not of type list().
            ValueError: Raised if list is empty.

        Returns:
            list: Returns a list of Food objects.
        """
        toReturn = []

        if not isinstance(dataList, list): raise TypeError("dataList must be of type list().")
        if len(dataList) <= 0: return []
        
        for item in dataList:
            toReturn.append(cls.fromDictionary(item))
        
        return toReturn

    @staticmethod
    def toDict(food, removeBarcode=True):
        """Converts Food object attributes into key: value pairs.

        Args:
            food (Food object): Food object to convert.
            removeBarcode (bool, optional): Removes barcode attribute when set True. Defaults to True.

        Returns:
            dict: Food object attributes as key: value pairs.
        """
        objData = {}
        if not isinstance(food, Food): raise TypeError("food must be of type Food().")

        for item in vars(food):
            if item == "servingSizeUom":
                objData[item] = ServingUom.toDict(getattr(food, item))
            else:
                objData[item] = getattr(food, item)
        
        if removeBarcode:
            objData.pop("barcode", None)
        return objData
    
            

class CaloriePal(object):
    DEFAULT_FOOD_SAVE_DATA = {
                        'servingUoms':
                        [
                            {'name': 'Grams', 'code': 'g'},
                            {'name': 'Pounds', 'code': 'lbs'},
                            {'name': 'Ounce', 'code': 'oz'}
                        ],
                    'foodData': {}
    }

    DEFAULT_SETTINGS = {
        'foodDataSaveLocation': ''
    }

    def __init__(self):
        """Creates a CaloriePal object.
        """
        self.foodData = {}
        self.servingUoms = []
        self.settings = {}
        self.foodDataFileOk = False

        self.foodDataFilePath = "FoodData.json"
        self.settingsFilePath = "Settings.json"

        self.readSettingsFile()
        self.readFoodDataFile()

    def readSettingsFile(self):
        """Reads settings file saved on disk.
        """
        data = {}

        if os.path.exists(self.settingsFilePath):
            with open(self.settingsFilePath, mode="r") as f:
                try:
                    data = json.loads(f.read())
                except json.JSONDecodeError:
                    data = CaloriePal.DEFAULT_SETTINGS
        else:
            data = CaloriePal.DEFAULT_SETTINGS
        
        self.settings = data

        if self.settings['foodDataSaveLocation'] != "" and os.path.exists(self.settings['foodDataSaveLocation']):
            self.foodDataFilePath = self.settings['foodDataSaveLocation']
    
    def saveSettingsFile(self):
        """Saves settings data to disk.
        """
        data = {}
        data = self.settings

        with open(self.settingsFilePath, mode="w") as f:
            f.write(json.dumps(data))


    def readFoodDataFile(self):
        """Reads food data file saved on disk.
        """
        data = {}

        if os.path.exists(self.foodDataFilePath):
            with open(self.foodDataFilePath, mode="r") as f:
                try:
                    data = json.loads(f.read())
                    self.foodDataFileOk = True
                except json.JSONDecodeError:
                    data = CaloriePal.DEFAULT_FOOD_SAVE_DATA
                    self.foodDataFileOk = False
        else:
            data = CaloriePal.DEFAULT_FOOD_SAVE_DATA
            self.foodDataFileOk = False

        rawFoodData = data["foodData"]
        self.foodData = {}

        if len(rawFoodData) > 0:
            for barcode in rawFoodData:
                foodObjData = rawFoodData[barcode]
                foodObjData['barcode'] = barcode
                
                self.foodData[barcode] = Food.fromDictionary(foodObjData)

        self.servingUoms = ServingUom.fromDictionaryList(data["servingUoms"])

    def getFoodDataJson(self, returnAsString=False):
        """Creates data structure for saving food data to disk.

        Args:
            returnAsString (bool, optional): Returns data as a string when True, otherwise returns a dictionary. Defaults to False.

        Returns:
            dict: Dictionary containing all food data to save.
        """
        data = {}

        data["servingUoms"] = []
        for uom in self.servingUoms:
            data["servingUoms"].append(ServingUom.toDict(uom))

        data["foodData"] = {}

        for barcode in self.foodData:
            data["foodData"][barcode] = Food.toDict(self.foodData[barcode])
        
        return data

    def saveFoodDataFile(self):
        """Saves food data to disk.
        """
        data = self.getFoodDataJson()

        with open(self.foodDataFilePath, mode="w") as f:
            f.write(json.dumps(data, indent=4))

    def changeFoodDataFile(self, newFilePath):
        """Changes food data file path and try's to reload file from new path.

        Args:
            newFilePath (string): Path to the new data file.

        Returns:
            tuple: Returns a tuple pair in the following way (bool, string). Where bool is True if change was successful and a message
                string of what ocurred.
        """

        msg = "Data file changed and reloaded successfully."

        if not os.path.exists(newFilePath):
            msg = "File path provided does not exists or file is corrupted."
            return (False, msg)

        oldFileOkStatus = self.foodDataFileOk
        oldFilePath = self.foodDataFilePath

        newFileOkStatus = False

        self.foodDataFilePath = newFilePath

        try:
            self.readFoodDataFile()
            newFileOkStatus = self.foodDataFileOk
        except Exception as err:
            fileChangeError = err
            newFileOkStatus = False
        
        if oldFileOkStatus == True and newFileOkStatus == False:
            self.foodDataFilePath = oldFilePath
            self.readFoodDataFile()
            msg = f"New data file failed to load in with error: {fileChangeError}"
            return (False, msg)
        
        else:
            self.settings["foodDataSaveLocation"] = newFilePath
            return (True, msg)






    def addFood(self, food):
        """Adds a new food to database.

        Args:
            food (Food Object): Food object to add.

        Raises:
            TypeError: Raised if object passed is not of type Food().
        """
        if not isinstance(food, Food): raise TypeError("Must be of class Food()")
        if food.barcode in self.foodData: return
        self.foodData[food.barcode] = food

        self.saveFoodDataFile()
    
    def updateFood(self, food):
        """Updates an existing food, calls addFood() if barcode not found.

        Args:
            food (Food Object): Food object to update.

        Raises:
            TypeError: Raised if object passed is not of type Food().
        """
        if not isinstance(food, Food): raise TypeError("Must be of class Food()")
        if food.barcode not in self.foodData:
            self.addFood(food)
            return

        self.foodData[food.barcode] = Food.toDict(food)

        self.saveFoodDataFile()
    
    def removeFood(self, food):
        """Removes a food using barcode value.

        Args:
            food (Food Object): Food object to remove.

        Raises:
            TypeError: Raised if object passed is not of type Food().
        """
        if not isinstance(food, Food): raise TypeError("Must be of class Food()")
        self.foodData.pop(food.barcode, None)

        self.saveFoodDataFile()
    
    def findFoodDataByBarcode(self, barcode):
        """Looks for a food item with barcode provided.

        Args:
            barcode (string): Barcode string to find.

        Returns:
            Food Object: Returns Food object matching barcode. Returns None if not found.
        """
        if barcode in self.foodData:
            return self.foodData[barcode]
        else:
            return None
        
    def findUomByName(self, uomName):
        """Looks for a ServingUom object matching the UOM name provided.

        Args:
            uomName (str): UOM name to find

        Returns:
            ServingUom: Returns ServingUom object matching name. Returns None if not found.
        """
        foundUom = None

        for x, uom in enumerate(self.servingUoms):
            if uomName == uom.name:
                foundUom = self.servingUoms[x]
                break
        
        return foundUom

    def addUom(self, uom):
        if not isinstance(uom, ServingUom): raise TypeError("Must be of class ServingUom()")
        self.servingUoms.append(uom)
        return


if __name__ == "__main__":
    calPal = CaloriePal()
    servingUom = calPal.servingUoms[0]

    f = Food("123456789", "Test Food", "Test Description", 170, 28, servingUom)

    calPal.addFood(f)

    calPal.saveFoodDataFile()