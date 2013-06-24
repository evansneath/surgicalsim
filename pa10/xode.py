__author__ = 'Evan Sneath, evansneath@gmail.com'

from pybrain.rl.environments.ode.tools.xodetools import XODEfile

class Pa10Xode(XODEfile):
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
        s1_size = [0.220, 0.315, 0.220]
        s1_pos = [0., y_floor+(s1_size[1]/2), 0.]
        s1_euler = [0., 0., 0.]
        s1_mass = 1.#100

        self.insertBody(bname='pa10_s1', shape='box',
                size=s1_size, density=0., pos=s1_pos,
                passSet=['arm'], euler=s1_euler, mass=s1_mass)

        # Fix the base of the robot to the environment. This prevents tipping
        self.affixToEnvironment('pa10_s1')

        # Create the S2 (Shoulder) segment
        s2_size = [0.094, 0.450, 0.094]
        s2_pos = [0., y_floor+s1_size[1]+(s2_size[1]/2), 0.]
        s2_euler = [0., 0., 0.]
        s2_mass = 1.#20

        self.insertBody(bname='pa10_s2', shape='box',
                size=s2_size, density=0., pos=s2_pos,
                passSet=['arm'], euler=s2_euler, mass=s2_mass)

        # Create a joint between S1 and S2
        self.insertJoint('pa10_s1', 'pa10_s2', type='hinge',
                axis={'x':0, 'y':0, 'z':1}, anchor=(0., y_floor+s1_size[1], 0.))

        # Add a cylinder at the joint to make it look better
        j1_size = [s1_size[0]/2, s1_size[0]]
        j1_pos = [0., y_floor+s1_size[1], 0.]
        j1_euler = [0., 0., 0.]
        j1_mass = 0.1

        self.insertBody(bname='pa10_j1', shape='cylinder',
                size=j1_size, density=0., pos=j1_pos,
                passSet=['arm'], euler=j1_euler, mass=j1_mass)

        # Attach J1 to S1
        self.insertJoint('pa10_j1', 'pa10_s1', type='fixed')

        # Add a white ring at the joint to see the joint direction better
        j2_size = [j1_size[0]+0.001, 0.01]
        j2_pos = j1_pos
        j2_euler = [0., 0., 0.]
        j2_mass = 0.1
        j2_color = (255, 255, 255, 255)

        self.insertBody(bname='pa10_j2', shape='cylinder',
                size=j2_size, density=0., pos=j2_pos,
                passSet=['arm'], euler=j2_euler, mass=j2_mass, color=j2_color)

        # Attach J2 to S1
        self.insertJoint('pa10_j2', 'pa10_s1', type='fixed')

        # Create the E1 (Elbow) segment
        e1_size = [0.0585, 0.500, 0.0585]
        e1_pos = [0., y_floor+s1_size[1]+s2_size[1]+(e1_size[1]/2), 0.]
        e1_euler = [0., 0., 0.]
        e1_mass = 1#15

        self.insertBody(bname='pa10_e1', shape='box',
                size=e1_size, density=0., pos=e1_pos,
                passSet=['arm'], euler=e1_euler, mass=e1_mass)

        # Create a joint between S2 and E1
        self.insertJoint('pa10_s2', 'pa10_e1', type='hinge',
                axis={'x':0, 'y':0, 'z':1},
                anchor=(0., y_floor+s1_size[1]+s2_size[1], 0.))

        # Add a cylinder at the joint to make it look better
        j3_size = [s2_size[0]/2, s2_size[0]]
        j3_pos = [0., y_floor+s1_size[1]+s2_size[1], 0.]
        j3_euler = [0., 0., 0.]
        j3_mass = 0.1

        self.insertBody(bname='pa10_j3', shape='cylinder',
                size=j3_size, density=0., pos=j3_pos,
                passSet=['arm'], euler=j3_euler, mass=j3_mass)

        # Attach J3 to S2
        self.insertJoint('pa10_j3', 'pa10_s2', type='fixed')

        # Add a white ring at the joint to see the joint direction better
        j4_size = [j3_size[0]+0.001, 0.01]
        j4_pos = j3_pos
        j4_euler = [0., 0., 0.]
        j4_mass = 0.1
        j4_color = (255, 255, 255, 255)

        self.insertBody(bname='pa10_j4', shape='cylinder',
                size=j4_size, density=0., pos=j4_pos,
                passSet=['arm'], euler=j4_euler, mass=j4_mass, color=j4_color)

        # Attach J4 to S2
        self.insertJoint('pa10_j4', 'pa10_s2', type='fixed')

        # Create the W1 (Wrist) segment
        w1_size = [0.043, 0.08, 0.043]
        w1_pos = [0., y_floor+s1_size[1]+s2_size[1]+e1_size[1]+(w1_size[1]/2), 0.]
        w1_euler = [0., 0., 0.]
        w1_mass = 1#10

        self.insertBody(bname='pa10_w1', shape='box',
                size=w1_size, density=0., pos=w1_pos,
                passSet=['arm'], euler=w1_euler, mass=w1_mass)

        # Create a joint between E1 and W1
        self.insertJoint('pa10_e1', 'pa10_w1', type='hinge',
                axis={'x':0, 'y':0, 'z':1},
                anchor=(0., y_floor+s1_size[1]+s2_size[1]+e1_size[1], 0.))

        # Add a cylinder at the joint to make it look better
        j5_size = [e1_size[0]/2, e1_size[0]]
        j5_pos = [0., y_floor+s1_size[1]+s2_size[1]+e1_size[1], 0.]
        j5_euler = [0., 0., 0.]
        j5_mass = 0.1

        self.insertBody(bname='pa10_j5', shape='cylinder',
                size=j5_size, density=0., pos=j5_pos,
                passSet=['arm'], euler=j5_euler, mass=j5_mass)

        self.insertJoint('pa10_j5', 'pa10_e1', type='fixed')

        # Add a white ring at the joint to see the joint direction better
        j6_size = [j5_size[0]+0.001, 0.01]
        j6_pos = j5_pos
        j6_euler = [0., 0., 0.]
        j6_mass = 0.1
        j6_color = (255, 255, 255, 255)

        self.insertBody(bname='pa10_j6', shape='cylinder',
                size=j6_size, density=0., pos=j6_pos,
                passSet=['arm'], euler=j6_euler, mass=j6_mass, color=j6_color)

        # Attach J6 to E1
        self.insertJoint('pa10_j6', 'pa10_e1', type='fixed')

        # Create a tooltip to navigate through the gates
        t1_size = [0.005, 0.05]
        t1_pos = [0., y_floor+s1_size[1]+s2_size[1]+e1_size[1]+w1_size[1]+(t1_size[1]/2), 0.]
        t1_euler = [90., 0., 0.]
        t1_mass = 0.1
        t1_color = (255, 0, 0, 255) # red

        self.insertBody(bname='pa10_t1', shape='cylinder',
                size=t1_size, density=0., pos=t1_pos,
                passSet=['arm'], euler=t1_euler, mass=t1_mass, color=t1_color)

        # Attach J6 to E1
        self.insertJoint('pa10_t1', 'pa10_w1', type='fixed')

        # Create the world
        self.insertFloor(y=y_floor)

        # Focus on the base of the arm
        self.centerOn('pa10_s1')

        return


class Pa10StickXode(Pa10Xode):
    def __init__(self, name, **kwargs):
        """Adds a stick for the PA-10 arm to interact with."""
        Pa10Xode.__init__(self, name, **kwargs)

        y_floor = -1.5

        self.insertBody(bname='ball', shape='sphere',
                size=[0.06], density=0., pos=[0.8, y_floor+0.5, 0.0],
                passSet=['arm'], euler=[0., 0., 0.], mass=0.1)

        # Fix the base of the robot to the environment. This prevents tipping
        self.insertJoint('pa10_s1', 'ball', type='fixed')


        return
