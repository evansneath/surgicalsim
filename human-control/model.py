#!/usr/bin/env python

from pybrain.rl.environments.ode.tools.xodetools import XODEfile
import numpy as np


class EndEffectorModel(XODEfile):
    def __init__(self, name, **kwargs):
        XODEfile.__init__(self, name, **kwargs)

        y_floor = -1.0

        # Define the stick properties
        m_stick = 1.0
        l_stick = 0.1
        w_stick = 0.005

        siz_stick = [w_stick, l_stick]
        pos_stick = [0.0, y_floor+0.4, 0.0]
        eul_stick = [90.0, 0.0, 0.0]

        self.insertBody(bname='stick', shape='cylinder', size=siz_stick,
                density=0.0, pos=pos_stick, passSet=['end_effector'],
                euler=eul_stick, mass=m_stick)

        m_tooltip = 0.1
        r_tooltip = 0.01

        siz_tooltip = [r_tooltip]
        pos_tooltip = [0.0, y_floor+0.4-(l_stick/2.0), 0.0]
        eul_tooltip = [0.0, 0.0, 0.0]

        self.insertBody(bname='tooltip', shape='sphere', size=siz_tooltip,
                density=0.0, pos=pos_tooltip, passSet=['end_effector'],
                euler=eul_stick, mass=m_tooltip, color=(255, 0, 0, 255))

        self.insertJoint('stick', 'tooltip', type='fixed')

        m_table = 1.0
        siz_table = [0.3, 0.01, 0.3]
        pos_table = [0.0, y_floor+0.2, 0.0] 
        eul_table = [0.0, 0.0, 0.0]

        self.insertBody(bname='table', shape='box', size=siz_table,
                density=0.0, pos=pos_table, passSet=[],
                euler=eul_table, mass=m_table)

        # Insert the floor position and center the camera
        self.insertFloor(y=y_floor)
        self.centerOn('table')

        self.affixToEnvironment('table')

        return

   

class TestArmModel(XODEfile):
    def __init__(self, name, **kwargs):
        XODEfile.__init__(self, name, **kwargs)

        y_floor = -1.0

        # Define an x position indicator
        mx = 1.0
        x_siz = [1.0, 0.1, 0.1]
        x_pos = [0.5, y_floor+0.1/2.0, 0.0]
        x_eul = [0.0, 0.0, 0.0]

        # Add body objects to the XODE file
        self.insertBody(bname='x_ptr', shape='box', size=x_siz, density=0.0,
                pos=x_pos, passSet=['arm'], euler=x_eul, mass=mx)


        # Define base
        m0 = 1.0 # [kg]
        l0 = 0.5 # [m]
        lc0 = l0 / 2.0 # [m]
        omega0 = 0.0

        l0_siz = np.array([0.1, l0])
        l0_pos = np.array([0.0, y_floor+lc0, 0.0])
        l0_eul = np.array([90.0, 0.0, omega0])

        l0_end_pos = np.array([0.0, y_floor+l0, 0.0])

        # Define link 1
        m1 = 1.0 # [kg]
        l1 = 1.0 # [m]
        lc1 = l1 / 2.0 # [m]
        omega1 = 45.0 # [deg]

        l1_siz = np.array([0.1, l1])
        l1_pos = np.array([
            l0_end_pos[0]+lc1*np.cos(np.radians(omega1)),
            l0_end_pos[1]+lc1*np.sin(np.radians(omega1)),
            0.0
        ])
        l1_eul = l0_eul + np.array([0.0, 0.0, omega1])

        l1_end_pos = l0_end_pos + np.array([
            l1*np.cos(np.radians(omega1)),
            l1*np.sin(np.radians(omega1)),
            0.0
        ])

        # Define link 2
        m2 = 1.0 # [kg]
        l2 = 1.0 # [m]
        lc2 = l2 / 2.0 # [m]
        omega2 = 20.0 # [deg]

        l2_siz = np.array([0.1, l2])
        l2_pos = l1_end_pos + np.array([
                lc2*np.cos(np.radians(omega2)),
                lc2*np.sin(np.radians(omega2)),
                0.0
        ])
        l2_eul = l1_eul + np.array([0.0, 0.0, omega2])

        l2_end_pos = l1_end_pos + np.array([
                l2*np.cos(np.radians(omega2)),
                l2*np.sin(np.radians(omega2)),
                0.0
        ])

        # Add body objects to the XODE file
        self.insertBody(bname='l0', shape='cylinder', size=l0_siz, density=0.0,
                pos=l0_pos, passSet=['arm'], euler=l0_eul, mass=m0)

        self.insertBody(bname='l1', shape='cylinder', size=l1_siz, density=0.0,
                pos=l1_pos, passSet=['arm'], euler=l1_eul, mass=m1)

        self.insertBody(bname='l2', shape='cylinder', size=l2_siz, density=0.0,
                pos=l2_pos, passSet=['arm'], euler=l2_eul, mass=m2)

        # Define joints between links in the XODE file
        self.insertJoint('l0', 'l1', type='hinge',
                axis={'x':0, 'y':0, 'z':1}, anchor=tuple(l0_end_pos))

        self.insertJoint('l1', 'l2', type='hinge',
                axis={'x':0, 'y':0, 'z':1}, anchor=tuple(l1_end_pos))

        # Fix the base to the environment
        self.affixToEnvironment('l0')

        # Insert the floor position and center the camera
        self.insertFloor(y=y_floor)
        self.centerOn('l1')

        return
