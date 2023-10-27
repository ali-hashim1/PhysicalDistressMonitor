import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np

csv_file = 'Heart Rate Data-manual (4).csv'
df = pd.read_csv(csv_file)

df['Height'] = df['Height'] /272 #max human height
df['Age'] = df['Age'] /100 # average max age
df['Pulse'] = df['Pulse'] /300 #maximum human pulse
df['Temp'] = df['Temp'] /116 #maximum human temperature
df['Oxygen'] = df['Oxygen'] /100 #maximum human oxygen

X = df[df.columns[:-1]].values
Y = df[df.columns[-1]].values

test_data1 = np.array([[1,0,0.69,0.21,0.0,0.84,0.99]])
test_labels1 = np.array([[0]])

test_data2 = np.array([[1,0,0.69,0.21,0.5,0.0,0.99]])
test_labels2 = np.array([[0]])

test_data3 = np.array([[1,0,0.69,0.21,0.5,0.84,0.0]])
test_labels3 = np.array([[0]])

test_data4 = np.array([[1,0,0.69,0.21,0.5,0.84,0.99]])
test_labels4 = np.array([[1]])


model = keras.Sequential([
                keras.layers.Dense(5, activation="sigmoid"),
                keras.layers.Dense(10, activation="sigmoid"),
                keras.layers.Dense(5, activation="sigmoid"),
                keras.layers.Dense(1, activation="sigmoid")
            ])
model.compile(loss="mean_squared_error", metrics=["accuracy"])
model.fit(X, Y, epochs=20)

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

model.save('phyiscal_risk_prediction.keras')
