__author__ = 'Evan Sneath, evansneath@gmail.com'

"""
Code modified from PyBrain CCRLGlas example model.
"""

from pybrain.rl.environments.ode import ODEEnvironment, sensors, actuators
import imp
import xode
import ode
import sys
from scipy import array, asarray

class Pa10Environment(ODEEnvironment):
    def __init__(self, xodeFile="./pa10.xode", renderer=True, realtime=False, ip="127.0.0.1", port="21590", buf='16384'):
        ODEEnvironment.__init__(self, renderer, realtime, ip, port, buf)

        # Load model file
        self.pert = array([0.0, 0.0, 0.0])
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
        s2_angle = 1.#0.25
        e1_angle = 1.#0.38
        w1_angle = 1.#0.45

        # Set joint max/min rotation angles
        self.cHighList = array([s2_angle, e1_angle, w1_angle])
        self.cLowList = array([-s2_angle, -e1_angle, -w1_angle])

        self.stepsPerAction = 1

#    def step(self):
#        # Detect collisions and create contact joints
#        self.tableSum = 0
#        self.glasSum = 0
#        ODEEnvironment.step(self)
#
#    def _near_callback(self, args, geom1, geom2):
#        """Callback function for the collide() method.
#        This function checks if the given geoms do collide and
#        creates contact joints if they do."""
#
#        # only check parse list, if objects have name
#        if geom1.name != None and geom2.name != None:
#            # Preliminary checking, only collide with certain objects
#            for p in self.passpairs:
#                g1 = False
#                g2 = False
#                for x in p:
#                    g1 = g1 or (geom1.name.find(x) != -1)
#                    g2 = g2 or (geom2.name.find(x) != -1)
#                if g1 and g2:
#                    return()
#
#        # Check if the objects do collide
#        contacts = ode.collide(geom1, geom2)
#        tmpStr = geom2.name[:-2]
#        handStr = geom1.name[:-1]
#        if geom1.name == 'plate' and tmpStr != 'objectP':
#            self.tableSum += len(contacts)
#        if tmpStr == 'objectP' and handStr == 'pressLeft':
#            if len(contacts) > 0: self.glasSum += 1
#        tmpStr = geom1.name[:-2]
#        handStr = geom2.name[:-1]
#        if geom2.name == 'plate' and tmpStr != 'objectP':
#            self.tableSum += len(contacts)
#        if tmpStr == 'objectP' and handStr == 'pressLeft':
#            if len(contacts) > 0: self.glasSum += 1
#
#        # Create contact joints
#        world, contactgroup = args
#        for c in contacts:
#            p = c.getContactGeomParams()
#            # parameters from Niko Wolf
#            c.setBounce(0.2)
#            c.setBounceVel(0.05) #Set the minimum incoming velocity necessary for bounce
#            c.setSoftERP(0.6) #Set the contact normal "softness" parameter
#            c.setSoftCFM(0.00005) #Set the contact normal "softness" parameter
#            c.setSlip1(0.02) #Set the coefficient of force-dependent-slip (FDS) for friction direction 1
#            c.setSlip2(0.02) #Set the coefficient of force-dependent-slip (FDS) for friction direction 2
#            c.setMu(self.FricMu) #Set the Coulomb friction coefficient
#            j = ode.ContactJoint(world, contactgroup, c)
#            j.name = None
#            j.attach(geom1.getBody(), geom2.getBody())

#    def reset(self):
#        ODEEnvironment.reset(self)
#        self.pert = asarray([1.5, 0.0, 1.0])

if __name__ == '__main__' :
    w = Pa10Environment()
    while True:
        w.step()
