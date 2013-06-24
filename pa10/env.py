__author__ = 'Evan Sneath, evansneath@gmail.com'

"""
Code modified from PyBrain CCRLGlas example model.
"""

from pybrain.rl.environments.ode import ODEEnvironment, sensors, actuators
from scipy import array


class Pa10Environment(ODEEnvironment):
    def __init__(self, xodeFile="./pa10.xode", renderer=True, realtime=False, ip="127.0.0.1", port="21590", buf='16384'):
        ODEEnvironment.__init__(self, renderer, realtime, ip, port, buf)

        # Load model file
        #self.pert = array([0.0, 0.0, 0.0])
        self.loadXODE(xodeFile)

        # Standard sensors and actuators
        self.addSensor(sensors.JointSensor())
        self.addSensor(sensors.JointVelocitySensor())
        self.addActuator(actuators.JointActuator())

        # Set number of actuators and sensors (observers)
        self.actLen = self.indim
        self.obsLen = self.outdim

        #print 'NUM ACTUATORS: %d' % self.actLen
        #print self.getActuatorNames()
        #print 'NUM SENSORS: %d' % self.obsLen
        #print self.getSensorNames()

        # The torque values for the joints are normalized from the max torque in the env
        self.torque_max = 5.3

        torque_s2_pivot_norm = 5.3 / float(self.torque_max)
        torque_e1_pivot_norm = 2. / float(self.torque_max)
        torque_w1_pivot_norm = 0.36 / float(self.torque_max)

        # Set joint max torques
        torques = [torque_s2_pivot_norm, torque_e1_pivot_norm, torque_w1_pivot_norm]
        self.torqueList = array(torques)
        self.tourqueList = self.torqueList

        # Define joint max/min rotation angles (normalized by 360 degrees)
        s2_angle = 0.25
        e1_angle = 0.38
        w1_angle = 0.45

        # Set joint max/min rotation angles
        self.cHighList = array([s2_angle, e1_angle, w1_angle])
        self.cLowList = array([-s2_angle, -e1_angle, -w1_angle])

        self.stepsPerAction = 1


if __name__ == '__main__' :
    env = Pa10Environment()

    # Simulate this environment until the end of time
    while True:
        env.step()
