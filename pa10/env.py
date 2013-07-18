#!/usr/bin/env python

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

        # Set the gravity to none
        # TODO: This isn't modifying the gravity properly. See how this can be fixed
        # NOTE: At the moment, gravity is set to 0.0 in .../ode/environments.py
        #gravity = 0.0 #9.81
        #self.world.setGravity((0.0, gravity, 0.0))

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

        # PA-10 realistic max joint torques
        # s1 (rotate): 5.3
        # s2 (pivot) : 5.3
        # s3 (rotate): 2.0
        # e1 (pivot) : 2.0
        # e2 (rotate): 0.36
        # w1 (pivot) : 0.36
        # w2 (rotate): 0.36

        self.torque_max = 5.3

        torque_s1_rotate_norm = 5.3 / self.torque_max
        torque_s2_pivot_norm = 5.3 / self.torque_max

        torque_s3_rotate_norm = 2.0 / self.torque_max
        torque_e1_pivot_norm = 2.0 / self.torque_max

        torque_e2_rotate_norm = 0.36 / self.torque_max
        torque_w1_pivot_norm = 0.36 / self.torque_max
        torque_w2_rotate_norm = 0.36 / self.torque_max

        # Set joint max torques
        torques = [
            #torque_s1_rotate_norm,
            torque_s2_pivot_norm,
            torque_s3_rotate_norm,
            torque_e1_pivot_norm,
            torque_w1_pivot_norm,
        ]

        self.torqueList = array(torques)

        # PyBrain devs spelled "Torque" incorrectly... 'tourqueList' is a inherited attribute
        self.tourqueList = self.torqueList

        # NOTE: PyBrain accepts joint angles between -2pi and 2pi. Be sure
        # to convert all values in degrees to radians.

        # PA-10 realistic max/min joint angles [degrees]
        # (Found in PA-10 manual)
        # s1 (rotate): 177
        # s2 (pivot) : 91
        # s3 (rotate): 174
        # e1 (pivot) : 137
        # e2 (rotate): 255
        # w1 (pivot) : 165
        # w2 (rotate): 360

        # Define joint max/min rotation angles
        rotation = 360.0
        s1_angle = 177.0 / rotation
        s2_angle = 45.0 / rotation
        s2_angle *= 2.0 * pi

        s3_angle = 45.0 / rotation
        s3_angle *= 2.0 * pi

        e1_angle = 137.0 / rotation
        e1_angle *= 2.0 * pi

        e2_angle = 255.0 / rotation
        e2_angle *= 2.0 * pi

        w1_angle = 165.0 / rotation
        w1_angle *= 2.0 * pi

        w2_angle = 360.0 / rotation

        # Set joint max/min rotation angles
        self.cHighList = array([
            #s1_angle,
            s2_angle,
            s3_angle,
            e1_angle,
            w1_angle,
        ])

        self.cLowList = array([
            #0.0,
            0.0,
            -s3_angle,
            0.0,
            0.0,
        ])

        self.stepsPerAction = 1


if __name__ == '__main__' :
    env = Pa10Environment()

    # Simulate this environment until the end of time
    while True:
        env.step()
