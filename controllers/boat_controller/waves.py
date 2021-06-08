import pandas as pd

frontLoad_Forces = pd.read_csv('C:/Users/buiti/Desktop/UCLA/Capstone/controllers/boat_controller/frontLoadForcesMean.csv', usecols=[0, 1, 2], names=['front_Fx', 'front_Fy', 'front_Fz'])
frontLoad_Torques = pd.read_csv('C:/Users/buiti/Desktop/UCLA/Capstone/controllers/boat_controller/frontLoadTorquesMean.csv', usecols=[0, 1, 2], names=['front_Tx', 'front_Ty', 'front_Tz'])

sideLoad_Forces = pd.read_csv('C:/Users/buiti/Desktop/UCLA/Capstone/controllers/boat_controller/sideLoadForcesMean.csv', usecols=[0, 1, 2], names=['side_Fx', 'side_Fy', 'side_Fz'])
sideLoad_Torques = pd.read_csv("C:/Users/buiti/Desktop/UCLA/Capstone/controllers/boat_controller/sideLoadTorquesMean.csv", usecols=[0, 1, 2], names=['side_Tx', 'side_Ty', 'side_Tz'])

print(frontLoad_Forces.at[1, 'front_Fx'])
print(frontLoad_Forces.at[1, 'front_Fy'])
print(frontLoad_Forces.at[1, 'front_Fz'])

print(frontLoad_Torques.at[1, 'front_Tx'])
print(frontLoad_Torques.at[1, 'front_Ty'])
print(frontLoad_Torques.at[1, 'front_Tz'])