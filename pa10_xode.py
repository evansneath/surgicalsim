__author__ = 'Evan Sneath, evansneath@gmail.com'

from pybrain.rl.environments.ode.tools.xodetools import XODEfile

class XODEPA10(XODEfile):
    def __init__(self, name, **kwargs):
        """Creates a model representation of the Mitsubishi PA-10"""
        XODEfile.__init__(self, name, **kwargs)

        # Define the floor height relative to the camera (at [0,0,0]). The
        # floor will be added to the environment last.
        y_floor = -1.5

        # Create the Mitsubishi PA-10 robotic arm

        # NOTE: The position of the shape refers to its center. To accomodate
        # this, calculations are done to find relative position in the world

        # Create the S1 (Shoulder) segment
        s1_size = [0.220, 0.315]
        s1_pos = [0., y_floor+(s1_size[1]/2), 0.]
        s1_euler = [90., 0., 0.]
        s1_mass = 100

        self.insertBody(bname='pa10_s1', shape='cylinder',
                size=s1_size, density=0., pos=s1_pos,
                passSet=['arm'], euler=s1_euler, mass=s1_mass)

        # Fix the base of the robot to the environment. This prevents tipping
        self.affixToEnvironment('pa10_s1')

        # Create the S2 (Shoulder) segment
        s2_size = [0.094, 0.450, 0.094]
        s2_pos = [0., y_floor+s1_size[1]+(s2_size[1]/2), 0.]
        s2_euler = [0., 0., 0.]
        s2_mass = 20

        self.insertBody(bname='pa10_s2', shape='box',
                size=s2_size, density=0., pos=s2_pos,
                passSet=['arm'], euler=s2_euler, mass=s2_mass)

        # Join S1 and S2
        self.insertJoint('pa10_s1', 'pa10_s2', type='hinge',
                axis={'x':1, 'y':0, 'z':0}, anchor=(0., s1_size[1], 0.))

        # Add a sphere at the joint to make it look better
        j1_size = [s1_size[0]]
        j1_pos = [0., y_floor+s1_size[1], 0.]
        j1_euler = [0., 0., 0.]
        j1_mass = 0.1

        self.insertBody(bname='pa10_j1', shape='sphere',
                size=j1_size, density=0., pos=j1_pos,
                passSet=['arm'], euler=j1_euler, mass=j1_mass)

        # Join J1 to S1
        self.insertJoint('pa10_j1', 'pa10_s1', type='fixed')

        # Add a cylinder at the joint to see the joint direction better
        j2_size = [s1_size[0]+0.02, 0.01]
        j2_pos = [0., y_floor+s1_size[1], 0.]
        j2_euler = [0., 0., 0.]
        j2_mass = 0.1
        j2_color = (255, 255, 255, 255)

        self.insertBody(bname='pa10_j2', shape='cylinder',
                size=j2_size, density=0., pos=j2_pos,
                passSet=['arm'], euler=j2_euler, mass=j2_mass, color=j2_color)

        # Join J2 to S1
        self.insertJoint('pa10_j2', 'pa10_s1', type='fixed')

        # Create the E1 (Elbow) segment
        e1_size = [0.150, 0.500, 0.150]
        e1_pos = [0., y_floor+s1_size[1]+s2_size[1]+(e1_size[1]/2), 0.]
        e1_euler = [0., 0., 0.]
        e1_mass = 15

        self.insertBody(bname='pa10_e1', shape='box',
                size=e1_size, density=0., pos=e1_pos,
                passSet=['arm'], euler=e1_euler, mass=e1_mass)

        # Join S2 and E1
        self.insertJoint('pa10_s2', 'pa10_e1', type='hinge',
                axis={'x':1, 'y':0, 'z':0},
                anchor=(0., s1_size[1]+s2_size[1], 0.))

        # Create the world
        self.insertFloor(y=y_floor)

        self.centerOn('pa10_s1')

        # YARDSTICK TEST (FOR MEASURING STUFF)
        #test_size = [0.1, s1_size[1]+s2_size[1]+e1_size[1]]
        #self.insertBody(bname='test', shape='cylinder',
        #        size=test_size, density=0.,
        #        pos=[0.5, y_floor+(test_size[1]/2), 0.], euler=[90., 0, 0], mass=10.)

        return
