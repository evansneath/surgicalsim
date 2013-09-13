#!/usr/bin/env python

"""Model module

Contains the classes necessary for XODE file generation specific to the
Surgical Sim test article training simulation.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Classes:
    TrainingSimModel: Builds all objects used for the test article simulation.
"""

from pybrain.rl.environments.ode.tools.xodetools import XODEfile
import numpy as np


class TrainingSimModel(XODEfile):
    """TrainingSimModel class

    Generates the XODE file used for the ODE environment.

    Inherits:
        XODEfile: An xode file building class.

    Methods:
        generate: Generates the xode model of the world.
    """
    def __init__(self, name, randomize_test_article=False):
        """Initialize

        Creates a new TrainingSimModel object.

        Arguments:
            randomize_test_article: Determines if the test article to be
                generated will have randomized gates. (Default: False)
        """
        super(TrainingSimModel, self).__init__(name)

        self._name = name
        self._randomize_test_article = randomize_test_article

        return

    def generate(self):
        """Generate

        Generates the xode model of the world.
        """
        self.insertFloor(y=0.0)

        # Build the test article with gates
        y_top_table = build_test_article(self, self._randomize_test_article)

        # Build the training tooltip
        build_end_effector(self, y_top_table)

        # Build the Mitsubishi PA10 robotic arm
        # TODO: Move this to its own class
        build_pa10(self, 0.0, -1.0)

        self.writeXODE('./'+self._name)

        return


def build_end_effector(xode, y_offset):
    """Build End Effector

    Arguments:
        y_offset: The top of the table under the end effector. This is
            used to calculate relative positions to the test article.
    """
    y_pos_end_effector = y_offset + 0.1

    # Define the tooltip properties
    m_tooltip = 10.0 # [g]
    r_tooltip = 0.005 # [m]

    siz_tooltip = np.array([r_tooltip])
    pos_tooltip = np.array([0.0, y_pos_end_effector, 0.0])
    eul_tooltip = np.array([0.0, 0.0, 0.0])

    xode.insertBody(bname='tooltip', shape='sphere', size=siz_tooltip,
            density=0.0, pos=pos_tooltip, passSet=['end_effector'],
            euler=eul_tooltip, mass=m_tooltip, color=(255, 0, 0, 255),
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

    # Calculate the actual gate height [y]
    gate_height = gate_norm_height * gate_height_multiplier

    # Calculate the actual gate position [x, z]
    gate_pos = gate_norm_pos * gate_pos_multiplier

    # Calculate the actual gate rotation
    gate_rot = gate_norm_rot * gate_rot_multiplier

    if randomize:
        # Randomize gate height, position, rotation
        height_rand_limit = 0.04 # [m]
        pos_rand_limit = 0.03 # [m]
        rot_rand_limit = 20.0 * (np.pi / 180.0) # [rad]

        # Find the random offsets for each gate's attributes
        height_rand = height_rand_limit * ((np.random.rand(8) - 0.5) * 2.0)
        pos_rand = pos_rand_limit * ((np.random.rand(8, 2) - 0.5) * 2.0)
        rot_rand = rot_rand_limit * ((np.random.rand(8) - 0.5) * 2.0)

        # Offset the gate attributes
        gate_height += height_rand
        gate_pos += pos_rand
        gate_rot += rot_rand

    # Generate the gates at these positions
    for i in range(8):#range(8):
        build_gate(xode, i, y_top_table, gate_height[i], gate_pos[i],
                gate_rot[i])

    xode.affixToEnvironment('table')

    return y_top_table


def build_gate(xode, num, top_table, gate_height, gate_pos, gate_rot):
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
            color=(255, 255, 255, 255)
    )

    marker2_name = gate_name + '_marker2'
    marker2_pos = gate_full_pos - marker_offset

    xode.insertBody(bname=marker2_name, shape='sphere',
            size=marker_size, density=0.0, pos=marker2_pos,
            passSet=['test_article'], euler=marker_eul, mass=marker_mass,
            color=(255, 255, 255, 255)
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

    # Create fixed joints between all parts of the gate. This makes it
    # a single body
    xode.insertJoint(support_name, base_name, type='fixed')
    xode.insertJoint(stand1_name, support_name, type='fixed')
    xode.insertJoint(stand2_name, support_name, type='fixed')
    xode.insertJoint(marker1_name, stand1_name, type='fixed')
    xode.insertJoint(marker2_name, stand2_name, type='fixed')

    # Fix the gate to the test article table
    xode.insertJoint(base_name, 'table', type='fixed')

    return


def build_pa10(xode, x_offset, z_offset):
    pa10_passset = ['pa10']

    # Determine link 0 (base) paramters
    # TODO: Get an accurate measurement of this value
    l0_height = 0.195 # [m]
    l0_diameter = 0.220 # [m]
    l0_size = np.array([l0_diameter/2.0, l0_height]) # [m]
    # NOTE: This is an estimate of the mass of l0
    l0_mass = 8000.0 # [g]
    l0_pos = np.array([x_offset, l0_height/2.0, z_offset]) # [m]
    l0_eul = np.array([90.0, 0.0, 0.0])

    xode.insertBody(
            bname='pa10_l0',
            shape='cylinder',
            size=l0_size,
            density=0.0,
            pos=l0_pos,
            passSet=pa10_passset,
            euler=l0_eul,
            mass=l0_mass,
            color=(0.2, 0.2, 0.2, 1.0)
    )

    l0_top = l0_height

    # Determine link 1 parameters
    # NOTE: This is an estimation of the l1 mass parameter
    l1_mass = 2000.0

    # Define the l1 base parameters
    l1_base_height = 0.020 # [m]
    l1_base_diameter = l0_diameter

    l1_base_size = np.array([
        l1_base_diameter/2.0,
        l1_base_height
    ])

    l1_base_pos = np.array([
        x_offset,
        l0_top+(l1_base_height/2.0),
        z_offset
    ])
    
    # Define the l1 connectors parameters
    l1_connector_height = 0.190 # [m]
    l1_connector_width = 0.050 # [m]
    l1_connector_depth = 0.140 # [m]

    l1_connector_size = np.array([
        l1_connector_height,
        l1_connector_width,
        l1_connector_depth
    ])

    l1_connector_pos = np.array([
        x_offset,
        l0_top+(l1_connector_height/2.0),
        z_offset
    ])

    l1_connector_distance = 0.160 # [m]

    build_connector_joint(
            xode,
            name='pa10_l1',
            mass=l1_mass,
            passset=pa10_passset,
            connector_size=l1_connector_size,
            connector_pos=l1_connector_pos,
            connector_distance=l1_connector_distance,
            base_size=l1_base_size,
            base_pos=l1_base_pos,
            color=(0.5, 0.5, 0.5, 1.0)
    )

    l1_top = l0_top + l1_connector_height

    # TODO: Determine link 2 parameters
    # TODO: Determine link 3 parameters
    # TODO: Determine link 4 parameters
    # TODO: Determine link 5 parameters
    # TODO: Determine link 6 parameters
    # TODO: Determine link 7 parameters

    xode.insertJoint('pa10_l1', 'pa10_l0', type='fixed')

    return

def build_connector_joint(xode, name, mass, passset, connector_size,
        connector_pos, connector_distance, base_size, base_pos, color):
    """Build Connector Joint

    Construct a connector joint for the PA10 robotic arm.
    """
    # Determine base parameters
    base_name = name
    base_radius = base_size[0]
    base_height = base_size[1]

    # Calculate the volume of the base for mass distribution purposes
    base_volume = (np.pi * (base_radius) ** 2) * base_height

    # Calculate the volume of the connector for mass distribution purposes
    connector_cyl_volume = (connector_size[1] * ((np.pi *
                            (connector_size[2] / 2.0) ** 2) / 2.0))
    connector_box_volume = (connector_size[1] * (connector_size[0] -
                            connector_size[2]) * connector_size[2])
    connector_volume = (connector_cyl_volume * 2) + connector_box_volume

    total_volume = base_volume + (connector_volume * 2)

    # Calculate mass for each part based on volumes so all densities are equal
    base_mass = mass * (base_volume / total_volume)
    connector_mass = mass * (connector_volume / total_volume)

    # Determine first connector parameters
    connector1_name = name + '_connector1'
    connector1_pos = np.array([
        connector_pos[0]+(connector_distance/2.0)+(connector_size[1]/2.0),
        connector_pos[1],
        connector_pos[2]
    ])

    build_oblong_cylinder(
            xode,
            name=connector1_name,
            mass=connector_mass,
            passset=passset,
            size=connector_size,
            pos=connector1_pos,
            color=color
    )

    # Determine second connector parameters (copy of the first flipped over the
    # center position)
    connector2_name = name + '_connector2'
    connector2_pos = np.array([
        connector_pos[0]-(connector_distance/2.0)-(connector_size[1]/2.0),
        connector_pos[1],
        connector_pos[2]
    ])

    build_oblong_cylinder(
            xode,
            name=connector2_name,
            mass=connector_mass,
            passset=passset,
            size=connector_size,
            pos=connector2_pos,
            color=color
    )

    # Insert the base body into the system
    xode.insertBody(
            bname=base_name,
            shape='cylinder',
            size=base_size,
            density=0.0,
            pos=base_pos,
            passSet=passset,
            euler=[90.0, 0.0, 0.0],
            mass=base_mass,
            color=color
    )

    # Make fixed joints between the connectors and base
    xode.insertJoint(connector1_name, base_name, type='fixed')
    xode.insertJoint(connector2_name, base_name, type='fixed')

    return


def build_oblong_cylinder(xode, name, mass, passset, size, pos, color):
    """Build Oblong Cylinder

    Construct an oblong cylinder body.
    """
    height = size[0]
    width = size[1]
    depth = size[2]

    x = pos[0]
    y = pos[1]
    z = pos[2]

    box_name = name
    box_siz = np.array([depth, height-depth, width])
    box_pos = np.array([x, y, z])
    box_eul = np.array([0.0, 90.0, 0.0])

    up_cyl_name = name + '_cyl1'
    up_cyl_siz = np.array([depth/2.0, width])
    up_cyl_pos = np.array([x, y+(height/2.0)-(depth/2.0), z])
    up_cyl_eul = np.array([0.0, 90.0, 0.0])

    lo_cyl_name = name + '_cyl2'
    lo_cyl_siz = np.array([depth/2.0, width])
    lo_cyl_pos = np.array([x, y-(height/2.0)+(depth/2.0), z])
    lo_cyl_eul = np.array([0.0, 90.0, 0.0])

    cyl_volume = width * ((np.pi * (depth / 2.0) ** 2) / 2.0)
    box_volume = width * (height - depth) * depth
    total_volume = (cyl_volume * 2) + box_volume

    box_mass = mass * (box_volume / total_volume)
    up_cyl_mass = mass * (cyl_volume / total_volume)
    lo_cyl_mass = mass * (cyl_volume / total_volume)

    xode.insertBody(
            bname=box_name,
            shape='box',
            size=box_siz,
            density=0.0,
            pos=box_pos,
            passSet=passset,
            euler=box_eul,
            mass=box_mass,
            color=color
    )

    xode.insertBody(
            bname=up_cyl_name,
            shape='cylinder',
            size=up_cyl_siz,
            density=0.0,
            pos=up_cyl_pos,
            passSet=passset,
            euler=up_cyl_eul,
            mass=up_cyl_mass,
            color=color
    )

    xode.insertBody(
            bname=lo_cyl_name,
            shape='cylinder',
            size=lo_cyl_siz,
            density=0.0,
            pos=lo_cyl_pos,
            passSet=passset,
            euler=lo_cyl_eul,
            mass=lo_cyl_mass,
            color=color
    )

    xode.insertJoint(up_cyl_name, box_name, type='fixed')
    xode.insertJoint(lo_cyl_name, box_name, type='fixed')

    return


if __name__ == '__main__':
    pass
