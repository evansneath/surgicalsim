#!/usr/bin/env python

from pybrain.rl.environments.ode.tools.xodetools import XODEfile
import numpy as np


class HumanControlModel(XODEfile):
    def __init__(self, name, randomize_test_article=False, **kwargs):
        super(HumanControlModel, self).__init__(name, **kwargs)

        self.y_floor = -0.3
        self.insertFloor(y=self.y_floor)

        y_top_table = self.build_test_article(randomize_test_article)
        self.build_end_effector(y_top_table)

        self.affixToEnvironment('table')
       
        return


    def build_end_effector(self, y_top_table):
        """Build End Effector

        Arguments:
            y_top_table: The top of the table under the end effector. This is
                used to calculate relative positions to the test article.
        """
        y_pos_end_effector = y_top_table + 0.1

        # Define the tooltip properties
        m_tooltip = 1.0 # [kg]
        r_tooltip = 0.005 # [m]

        siz_tooltip = np.array([r_tooltip])
        pos_tooltip = np.array([0.0, y_pos_end_effector, 0.0])
        eul_tooltip = np.array([0.0, 0.0, 0.0])

        self.insertBody(bname='tooltip', shape='sphere', size=siz_tooltip,
                density=0.0, pos=pos_tooltip, passSet=['end_effector', 'test'],
                euler=eul_tooltip, mass=m_tooltip, color=(255, 0, 0, 255))

        # Define the stick properties
        m_stick = 1.0 # [kg]
        l_stick = 0.05 # [m]
        r_stick = 0.0025 # [m]

        siz_stick = np.array([r_stick, l_stick])
        pos_stick = pos_tooltip + np.array([0.0, l_stick/2.0, 0.0])
        eul_stick = np.array([90.0, 0.0, 0.0])

        self.insertBody(bname='stick', shape='cylinder', size=siz_stick,
                density=0.0, pos=pos_stick, passSet=['end_effector', 'test'],
                euler=eul_stick, mass=m_stick)

        self.insertJoint('stick', 'tooltip', type='fixed')

        return


    def build_test_article(self, randomize=True):
        y_pos_test_article = 0.001

        m_table = 1.0 # [kg]

        # Define the length of one side of the square table
        l_table = 0.4 # [m]

        # Define the height of the table
        h_table = 0.01 # [m]

        # Calculate the top of the table so gate generation is easier
        y_top_table = self.y_floor + h_table + y_pos_test_article

        siz_table = np.array([l_table, h_table, l_table])
        pos_table = np.array([
            0.0,
            self.y_floor+y_pos_test_article+(h_table/2.0),
            0.0,
        ])
        eul_table = np.array([0.0, 0.0, 0.0])

        # Build the table
        self.insertBody(bname='table', shape='box', size=siz_table,
                density=0.0, pos=pos_table, passSet=['test'],
                euler=eul_table, mass=m_table, color=(0.1, 0.1, 0.1, 0.6))

        # Define the normalized gate height for each gate [y]
        gate_norm_height = np.ones(8)

        # Keep the standard height of each gate at 10 cm off the board
        gate_height_multiplier = 0.10

        # Define standard normalized gate positions for each gate [x, z]
        gate_norm_pos = np.array([
            [-1, -1],
            [-1,  0],
            [-1,  1],
            [ 0,  1],
            [ 1,  1],
            [ 1,  0],
            [ 1, -1],
            [ 0, -1],
        ])

        # Define the normalization factor of position for each gate
        gate_pos_multiplier = (l_table / 2.0) * 0.8

        # Define standard normalized angles for each gate. Zero degrees is
        # along the positive X axis. Rotation is counter-clockwise. 1.0 is
        # 180 degrees (or pi radians) rotation
        gate_norm_rot = np.array([
            0.25,
            0.0,
            -0.25,
            -0.50,
            -0.75,
            -1.0,
            -1.25,
            -1.50,
        ])

        # Define the rotation multiplier to unnormalize the rotation value
        gate_rot_multiplier = np.pi

        # TODO: Randomize gate height, position, rotation

        # Calculate the actual gate height [y]
        gate_height = gate_norm_height * gate_height_multiplier

        # Calculate the actual gate position [x, z]
        gate_pos = gate_norm_pos * gate_pos_multiplier

        # Calculate the actual gate rotation
        gate_rot = gate_norm_rot * gate_rot_multiplier

        # Generate the gates at these positions
        for i in range(8):#range(8):
            self.build_gate(i, y_top_table, gate_height[i], gate_pos[i], gate_rot[i])

        return y_top_table


    def build_gate(self, num, top_table, gate_height, gate_pos, gate_rot):
        # Define the width of the gate entry point
        gate_width = 0.04

        gate_full_pos = np.array([
            gate_pos[0],
            top_table+gate_height,
            gate_pos[1],
        ])

        rot_matrix = np.array([
            np.cos(gate_rot), # x position normalizer
            1.0,              # y position normalizer (no rotation)
            np.sin(gate_rot), # z position normalizer
        ])

        gate_name = 'gate_' + str(num)

        marker_radius = 0.005
        marker_size = [marker_radius]
        marker_mass = 0.01
        marker_eul = np.array([0.0, 0.0, 0.0])

        marker_offset = rot_matrix * np.array([
            gate_width/2.0,
            0.0,
            gate_width/2.0,
        ])

        # Build the two markers on either side of the gate
        marker1_name = gate_name + '_marker1'
        marker1_pos = gate_full_pos + marker_offset

        self.insertBody(bname=marker1_name, shape='sphere',
                size=marker_size, density=0.0, pos=marker1_pos,
                passSet=['test'], euler=marker_eul, mass=marker_mass,
                color=(255, 255, 255, 255)
        )

        marker2_name = gate_name + '_marker2'
        marker2_pos = gate_full_pos - marker_offset

        self.insertBody(bname=marker2_name, shape='sphere',
                size=marker_size, density=0.0, pos=marker2_pos,
                passSet=['test'], euler=marker_eul, mass=marker_mass,
                color=(255, 255, 255, 255)
        )

        # Build the stands which hold the markers
        stand_size = np.array([
            marker_radius,
            gate_width,
        ])

        stand_mass = 0.02
        stand_eul = np.array([90.0, 0.0, 0.0])

        stand1_name = gate_name + '_stand1'
        stand1_pos = marker1_pos - np.array([0.0, stand_size[1]/2.0, 0.0])

        self.insertBody(bname=stand1_name, shape='cylinder',
                size=stand_size, density=0.0, pos=stand1_pos,
                passSet=['test'], euler=stand_eul, mass=stand_mass
        )

        stand2_name = gate_name + '_stand2'
        stand2_pos = marker2_pos - np.array([0.0, stand_size[1]/2.0, 0.0])

        self.insertBody(bname=stand2_name, shape='cylinder',
                size=stand_size, density=0.0, pos=stand2_pos,
                passSet=['test'], euler=stand_eul, mass=stand_mass
        )

        # Build the cross support
        support_name = gate_name + '_support'
        support_mass = 0.02

        support_size = np.array([
            gate_width+(2.0*stand_size[0]),
            2.0*stand_size[0],
            2.0*stand_size[0],
        ])

        support_pos = (gate_full_pos -
            np.array([0.0, gate_width+(support_size[1]/2.0), 0.0]))

        support_eul = np.array([0.0, gate_rot*180/np.pi, 0.0])

        self.insertBody(bname=support_name, shape='box',
                size=support_size, density=0.0, pos=support_pos,
                passSet=['test'], euler=support_eul, mass=support_mass
        )

        # Build the base for the gate
        base_name = gate_name + '_base'
        base_mass = 0.03 # [kg]

        base_size = np.array([
            0.005,
            gate_height-gate_width-support_size[1],
        ])

        base_pos = np.array([
            gate_pos[0],
            top_table+(base_size[1]/2.0),
            gate_pos[1],
        ])

        base_eul = np.array([90.0, 0.0, 0.0])

        self.insertBody(bname=base_name, shape='cylinder',
                size=base_size, density=0.0, pos=base_pos,
                passSet=['test'], euler=base_eul, mass=base_mass
        )

        self.insertJoint(base_name, 'table', type='fixed')

        return


class TestArmModel(XODEfile):
    def __init__(self, name, **kwargs):
        super(TestArmModel, self).__init__(name, **kwargs)

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
