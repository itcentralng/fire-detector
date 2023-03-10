import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier
from sklearn import tree
from joblib import dump

class FireDetectorModel:
    def __init__(self, features, 
                 normal_values, 
                 fire_values, 
                 dataset_size = 100, 
                 model = "svc", 
                 save_datasets = True) -> None:
        
        '''
        Initializes parameters for the detector, generates datasets, trains the model and calculates the accuracy

        Parameters
        ----------
        features: python list containing the names of the features
        normal_values: a single set of values when the sensor is not detecting fire
        fire_values: a single set of values when the sensor is detecting fire
        dataset_size: the size of the dataset to be generated
        model: the model to be used for training
        save_datasets: whether to save the generated datasets as csv files or not  
        '''
        
        self.features = features
        self.normal_values = normal_values
        self.fire_values = fire_values
        self.dataset_size = dataset_size
        self.model = model
        self.save_datasets = save_datasets
        self.make_dataframe(self.generate_dataset(normal_values), fire = False)
        self.make_dataframe(self.generate_dataset(fire_values), fire = True)
        self.merge_datasets()
        self.preprocess_data()
        self.train_model()
        

    def generate_dataset(self, array: list) -> np.ndarray:

        '''
        Generates a dataset of the given size by augmenting (adding noise to) the given array

        Parameters
        ----------
        array: a single set of values
        '''

        if isinstance(array, list):
            array = np.array(array)
            if array.ndim > 1:
                raise Exception("Array must be 1D")
            else:
                array = np.tile(array, (self.dataset_size, 1))
                noise = np.random.uniform(low = -1, high = 1, size = array.shape) * array
                return array + noise
                    
    def make_dataframe(self, array, fire) -> None:

        '''
        Creates a dataframe from the given array and adds a column for the target variable (fire or not)
        Saves the dataframe as a csv file if save_datasets is True

        Parameters
        ----------
        array: a numpy array containing the dataset (currently without the target variable)
        fire: a boolean value indicating whether the dataset is for fire or not
        '''

        df = pd.DataFrame(array, columns = self.features)
        df['Fire'] = [1 for i in range(len(df))] if fire else [0 for i in range(len(df))]
        if self.save_datasets: df.to_csv(f"dataset-{fire}.csv", index = False)
        self.df = df

    def merge_datasets(self) -> None:

        '''
        Merges the fire and non-fire datasets into a single dataframe and saves as a csv if save_datasets is True
        '''

        df1 = pd.read_csv("dataset-True.csv")
        df2 = pd.read_csv("dataset-False.csv")
        df = pd.concat([df1, df2], ignore_index = True)
        if self.save_datasets: df.to_csv("dataset.csv", index = False)
        self.df = df

    def preprocess_data(self) -> None:

        '''
        Split the dataset into training and testing sets
        '''

        X = self.df[self.features]
        y = self.df['Fire']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test

    def train_model(self) -> None:

        '''
        Trains the specified model and calculates the accuracy
        '''

        if self.model == "svc":
            model = SVC(kernel = 'rbf', C = 1, gamma = 'auto')
        elif self.model == "sgd":
            model = SGDClassifier(loss="hinge", penalty="l2", max_iter=5)
        elif self.model == "tree":
            model = tree.DecisionTreeClassifier()
        model.fit(self.X_train, self.y_train)
        dump(model, "model.joblib")
        self.accuracy = model.score(self.X_test, self.y_test) * 100

    def __repr__(self) -> str:

        '''
        Returns a string representation of the model
        '''
        
        return "Model: " + self.model + " Accuracy: " + str(self.accuracy) + "%"
    