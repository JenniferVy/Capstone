import numpy as np

# Based on https://jckantor.github.io/CBE30338/04.01-Implementing_PID_Control_with_Python_Yield_Statement.html
def PID(Kp, Ki, Kd): # TODO accept integrator limit as input
    # initial control
    PV, SP, dt = yield
    e = SP - PV
    
    P = Kp*e
    I = Ki*e*dt
    D = np.zeros(np.shape(Kd))
    
    MV = P + I + D
    
    e_prev = e
    
    while True:
        # yield MV, wait for new t, PV, SP
        PV, SP, dt = yield MV
        
        # PID calculations
        e = SP - PV
        
        P = Kp*e
        I = I + Ki*e*dt
        D = Kd*(e - e_prev)/dt
        
        MV = P + I + D
        
        # update stored data for next iteration
        e_prev = e
