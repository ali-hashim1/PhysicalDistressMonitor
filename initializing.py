import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np

csv_file = 'Initial Train Data - Random.csv'
df = pd.read_csv(csv_file)

df['Weight'] = df['Weight'] / 300 # avg max human weight for our user group
df['Height'] = df['Height'] /272 #max human height in cm
df['Age'] = df['Age'] /100 # average max age
df['Pulse'] = df['Pulse'] /300 #maximum human pulse
df['Temp'] = df['Temp'] /116 #maximum human temperature
df['Oxygen'] = df['Oxygen'] /100 #maximum human oxygen
df['Hydration'] = df['Hydration'] /512 #maximum hydration index

X = df[df.columns[:-1]].values
Y = df[df.columns[-1]].values

test_data1 = np.array([[1,0,0.66,0.69,0.21,0.0,0.84,0.99,0.78]]) #initializing test data for model acuracy testing
test_labels1 = np.array([[0]])

test_data2 = np.array([[1,0,0.66,0.69,0.21,0.5,0.0,0.99,0.78]])
test_labels2 = np.array([[0]])

test_data3 = np.array([[1,0,0.66,0.69,0.21,0.5,0.84,0.0,0.78]])
test_labels3 = np.array([[0]])

test_data4 = np.array([[1,0,0.66,0.69,0.21,0.5,0.84,0.99,0.78]])
test_labels4 = np.array([[1]])

#creating neural network, defining inputs, layers, and outputs
model = keras.Sequential([
                keras.layers.Dense(9, activation="relu"),
                keras.layers.Dense(12, activation="relu"),
                keras.layers.Dense(9, activation="relu"),
                keras.layers.Dense(1, activation="sigmoid")
            ])
#training model with collected data
model.compile(loss="binary_crossentropy", metrics=["accuracy"])
model.fit(X, Y, epochs=20)
#printing test results
test_acc = model.evaluate(test_data1, test_labels1)
print("Test Acc = ", test_acc)

prediction1 = model.predict(test_data1)
print("Target = ", 100*test_labels1, "Prediction = ", 100*prediction1)

prediction2 = model.predict(test_data2)
print("Target = ", 100*test_labels2, "Prediction = ", 100*prediction2)

prediction3 = model.predict(test_data3)
print("Target = ", 100*test_labels3, "Prediction = ", 100*prediction3)

prediction4 = model.predict(test_data4)
print("Target = ", 100*test_labels4, "Prediction = ", 100*prediction4)

model.save('keras/baseline.keras')
