import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np

csv_file = 'Retrain Data-randomized.csv'
df = pd.read_csv(csv_file)

df['Height'] = df['Height'] /272 #max human height
df['Age'] = df['Age'] /100 # average max age
df['Pulse'] = df['Pulse'] /300 #maximum human pulse
df['Temp'] = df['Temp'] /116 #maximum human temperature
df['Oxygen'] = df['Oxygen'] /100 #maximum human oxygen

X = df[df.columns[:-1]].values
Y = df[df.columns[-1]].values

test_data = np.array([[1,0,0.69,0.21,0.0,0.57,0.62]])
test_labels = np.array([[0]])

model = tf.keras.models.load_model('phyiscal_risk_prediction.keras')

model.fit(X, Y, epochs=20)

test_acc = model.evaluate(test_data, test_labels)
print("Test Acc = ", test_acc)

prediction = model.predict(test_data)
print("Target = ", 100*test_labels, "Prediction = ", 100*prediction)

model.save('phyiscal_risk_prediction.keras')