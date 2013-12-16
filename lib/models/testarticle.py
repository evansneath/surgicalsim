#!/usr/bin/env python

"""TestArticleModel module

Contains the classes necessary for XODE file generation specific to the
Surgical Sim test article training simulation.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Functions:
    build_end_effector: Given an XODE object, an end-effector will be built in
        the world.
    build_test_article: Given an XODE obejct, the test article platform will
        be built in the world.
"""

import numpy as np
import surgicalsim.lib.constants as constants


def build_end_effector(xode, y_offset):
    """Build End Effector

    Arguments:
        y_offset: The top of the table under the end effector. This is
            used to calculate relative positions to the test article.
    """
    # Determine position of the end effector (0.02 is half of gate width)
    y_pos_end_effector = y_offset + 0.1 - 0.02

    # Define the tooltip properties
    m_tooltip = 10.0 # [g]
    r_tooltip = 0.005 # [m]

    siz_tooltip = np.array([r_tooltip])
    pos_tooltip = np.array([0.0, y_pos_end_effector, 0.0])
    eul_tooltip = np.array([0.0, 0.0, 0.0])

    xode.insertBody(bname='tooltip', shape='sphere', size=siz_tooltip,
            density=0.0, pos=pos_tooltip, passSet=['end_effector'],
            euler=eul_tooltip, mass=m_tooltip, color=(1.0, 0.0, 0.0, 1.0),
            has_gravity=False)

    # Define the stick properties
    m_stick = 10.0 # [g]
    l_stick = 0.05 # [m]
    r_stick = 0.0025 # [m]

    siz_stick = np.array([r_stick, l_stick])
    pos_stick = pos_tooltip + np.array([0.0, l_stick/2.0, 0.0])
    eul_stick = np.array([90.0, 0.0, 0.0])

    xode.insertBody(bname='stick', shape='cylinder', size=siz_stick,
            density=0.0, pos=pos_stick, passSet=['end_effector'],
            euler=eul_stick, mass=m_stick, has_gravity=False)

    # Fix the joint between the stick and tooltip sphere
    xode.insertJoint('stick', 'tooltip', type='fixed')

    return


def build_test_article(xode, randomize=True):
    """Build Test Article

    Generates the test article used for training.

    Arguments:
        randomize: Determines if the gates of the test article should be
            randomized with position, height, and angle. (Default: True)
    """
    y_pos_test_article = 0.03

    m_table = 100.0 # [g]

    # Define the length of one side of the square table
    l_table = 0.4 # [m]

    # Define the height of the table
    h_table = 0.01 # [m]

    # Calculate the top of the table so gate generation is easier
    y_top_table = h_table + y_pos_test_article

    siz_table = np.array([l_table, h_table, l_table])
    pos_table = np.array([
        0.0,
        y_pos_test_article+(h_table/2.0),
        0.0,
    ])
    eul_table = np.array([0.0, 0.0, 0.0])

    # Build the table
    xode.insertBody(bname='table', shape='box', size=siz_table,
            density=0.0, pos=pos_table, passSet=['test_article'],
            euler=eul_table, mass=m_table, color=(0.1, 0.1, 0.1, 1.0))

    # Define the normalized gate height for each gate [y]
    gate_norm_height = np.ones(8)

    # Keep the standard height of each gate at 10 cm off the board
    gate_height_multiplier = 0.10

    # Define the normalization factor of position for each gate
    gate_pos_multiplier = (l_table / 2.0) * 0.8

    # Define standard normalized angles for each gate. Zero degrees is
    # along the positive X axis. Rotation is clockwise. 0.5 is 180 degrees
    # (or pi radians) rotation
    gate_norm_rot = constants.G_GATE_NORM_ROT + 0.25

    # Define the rotation multiplier to unnormalize the rotation value
    gate_rot_multiplier = 2.0 * np.pi

    # Calculate the actual gate height [y]
    gate_height = gate_norm_height * gate_height_multiplier

    # Calculate the actual gate position [x, z]
    gate_pos = constants.G_GATE_NORM_POS * gate_pos_multiplier

    # Calculate the actual gate rotation
    gate_rot = gate_norm_rot * gate_rot_multiplier

    if randomize:
        # Randomize gate height, position, rotation
        height_rand_limit = 0.0 # [m]
        pos_rand_limit = 0.025 # [m]
        rot_rand_limit = np.deg2rad(0.0) # [rad]

        # Find the random offsets for each gate's attributes
        height_rand = height_rand_limit * ((np.random.rand(8) - 0.5) * 2.0)
        pos_rand = pos_rand_limit * ((np.random.rand(8, 2) - 0.5) * 2.0)
        rot_rand = rot_rand_limit * ((np.random.rand(8) - 0.5) * 2.0)

        # Offset the gate attributes
        gate_height += height_rand
        gate_pos += pos_rand
        gate_rot += rot_rand

    # Generate the gates at these positions
    for i in range(constants.G_NUM_GATES):
        _build_gate(xode, i, y_top_table, gate_height[i], gate_pos[i],
                gate_rot[i])

    xode.affixToEnvironment('table')

    return y_top_table


def _build_gate(xode, num, top_table, gate_height, gate_pos, gate_rot):
    """Build Gate

    Arguments:
        num: The gate number to be appended to the name.
        top_table: The top of the table y position in [m].
        gate_height: The height of the gate to generate in [m].
        gate_pos: The 2-element numpy array of the [x, z] position of the
            gate to generate in [m].
        gate_rot: The rotation of the gate in [rad].
    """
    # Define the width of the gate entry point
    gate_width = 0.04

    top_table += 0.0001

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

    gate_name = 'gate' + str(num)

    marker_radius = 0.005
    marker_size = [marker_radius]
    marker_mass = 0.5
    marker_eul = np.array([0.0, 0.0, 0.0])

    marker_offset = rot_matrix * np.array([
        gate_width/2.0,
        0.0,
        gate_width/2.0,
    ])

    # Build the two markers on either side of the gate
    marker1_name = gate_name + '_marker1'
    marker1_pos = gate_full_pos + marker_offset

    xode.insertBody(bname=marker1_name, shape='sphere',
            size=marker_size, density=0.0, pos=marker1_pos,
            passSet=['test_article'], euler=marker_eul, mass=marker_mass,
            color=(1.0, 1.0, 1.0, 1.0)
    )

    marker2_name = gate_name + '_marker2'
    marker2_pos = gate_full_pos - marker_offset

    xode.insertBody(bname=marker2_name, shape='sphere',
            size=marker_size, density=0.0, pos=marker2_pos,
            passSet=['test_article'], euler=marker_eul, mass=marker_mass,
            color=(1.0, 1.0, 1.0, 1.0)
    )

    # Build the stands which hold the markers
    stand_size = np.array([
        marker_radius,
        gate_width,
    ])

    stand_mass = 2.0
    stand_eul = np.array([90.0, 0.0, 0.0])

    stand1_name = gate_name + '_stand1'
    stand1_pos = marker1_pos - np.array([0.0, stand_size[1]/2.0, 0.0])

    xode.insertBody(bname=stand1_name, shape='cylinder',
            size=stand_size, density=0.0, pos=stand1_pos,
            passSet=['test_article'], euler=stand_eul, mass=stand_mass
    )

    stand2_name = gate_name + '_stand2'
    stand2_pos = marker2_pos - np.array([0.0, stand_size[1]/2.0, 0.0])

    xode.insertBody(bname=stand2_name, shape='cylinder',
            size=stand_size, density=0.0, pos=stand2_pos,
            passSet=['test_article'], euler=stand_eul, mass=stand_mass
    )

    # Build the cross support
    support_name = gate_name + '_support'
    support_mass = 2.0

    support_size = np.array([
        gate_width+(2.0*stand_size[0]),
        2.0*stand_size[0],
        2.0*stand_size[0],
    ])

    support_pos = (gate_full_pos -
        np.array([0.0, gate_width+(support_size[1]/2.0), 0.0]))

    support_eul = np.array([0.0, gate_rot*180/np.pi, 0.0])

    xode.insertBody(bname=support_name, shape='box',
            size=support_size, density=0.0, pos=support_pos,
            passSet=['test_article'], euler=support_eul, mass=support_mass
    )

    # Build the base for the gate
    base_name = gate_name + '_base'
    base_mass = 3.0 # [g]

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

    xode.insertBody(bname=base_name, shape='cylinder',
            size=base_size, density=0.0, pos=base_pos,
            passSet=['test_article'], euler=base_eul, mass=base_mass
    )

    hitbox_name = gate_name
    hitbox_mass = 0.5 # [g]
    hitbox_size = np.array([
         gate_width,
         gate_height - base_size[1] - support_size[1],
         0.001,
    ])
    hitbox_pos = gate_full_pos - np.array([0.0, stand_size[1]/2.0, 0.0])
    hitbox_eul = np.array([0.0, gate_rot*180/np.pi, 0.0])

    xode.insertBody(bname=hitbox_name, shape='box',
            size=hitbox_size, density=0.0, pos=hitbox_pos,
            passSet=['end_effector', 'test_article'], euler=hitbox_eul,
            mass=hitbox_mass, invisible=True
    )

    # Create fixed joints between all parts of the gate. This makes it
    # a single body
    xode.insertJoint(hitbox_name, 'table', type='fixed')
    xode.insertJoint(support_name, base_name, type='fixed')
    xode.insertJoint(stand1_name, support_name, type='fixed')
    xode.insertJoint(stand2_name, support_name, type='fixed')
    xode.insertJoint(marker1_name, stand1_name, type='fixed')
    xode.insertJoint(marker2_name, stand2_name, type='fixed')

    # Fix the gate to the test article table
    xode.insertJoint(base_name, 'table', type='fixed')

    return


if __name__ == '__main__':
    pass
