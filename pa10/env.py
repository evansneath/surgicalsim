__author__ = 'Evan Sneath, evansneath@gmail.com'

"""
Code modified from PyBrain CCRLGlas example model.
"""

from pybrain.rl.environments.ode import ODEEnvironment, sensors, actuators
from scipy import array, pi


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

        torque_s1_rotate_norm = 1.0 / self.torque_max#5.3 / self.torque_max
        torque_s2_pivot_norm = 5.3 / self.torque_max

        torque_s3_rotate_norm = 2.0 / self.torque_max
        torque_e1_pivot_norm = 2.0 / self.torque_max

        torque_e2_rotate_norm = 0.36 / self.torque_max
        torque_w1_pivot_norm = 0.36 / self.torque_max
        torque_w2_rotate_norm = 0.36 / self.torque_max

        # Set joint max torques
        torques = [
            torque_s1_rotate_norm,
            torque_s2_pivot_norm,
            torque_e1_pivot_norm,
            torque_w1_pivot_norm
        ]

        self.torqueList = array(torques)

        # PyBrain devs spelled "Torque" incorrectly... torqueList is a inherited attribute
        self.tourqueList = self.torqueList

        # Define joint max/min rotation angles (normalized by 360 degrees)
        rotation = 360.0
        s1_angle = 300.0 / rotation #177.0 / rotation
        s2_angle =  91.0 / rotation
        s3_angle = 174.0 / rotation

        e1_angle = 137.0 / rotation
        e2_angle = 255.0 / rotation

        w1_angle = 165.0 / rotation
        w2_angle = 360.0 / rotation

        # Set joint max/min rotation angles
        self.cHighList = array([s1_angle, s2_angle, e1_angle, w1_angle])
        self.cLowList = array([-s1_angle, -s2_angle, -e1_angle, -w1_angle])

        self.stepsPerAction = 1


if __name__ == '__main__' :
    env = Pa10Environment()

    # Simulate this environment until the end of time
    while True:
        env.step()
