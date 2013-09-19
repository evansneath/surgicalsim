#!/usr/bin/env python

"""PA10Model module

Contains the classes necessary for XODE file generation specific to the
Surgical Sim PA10 simulation.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Functions:
    build_pa10: Given an XODE object, a PA10 robotic arm will be built in the
        world.
"""

import numpy as np


def build_pa10(xode, x_offset, z_offset):
    pa10_passset = ['pa10']

    dark_gray = (0.2, 0.2, 0.2, 1.0)
    light_gray = (0.5, 0.5, 0.5, 1.0)

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
            color=dark_gray
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

    # Build a 'U' shaped connector joint (all of l1)
    _build_connector_joint(
            xode,
            name='pa10_l1',
            mass=l1_mass,
            passset=pa10_passset,
            connector_size=l1_connector_size,
            connector_pos=l1_connector_pos,
            connector_distance=l1_connector_distance,
            base_size=l1_base_size,
            base_pos=l1_base_pos,
            color=light_gray
    )

    l1_top = l0_top + l1_connector_height

    # Determine link 2 parameters
    l2_mass = 8410.0 # [g]

    l2_joint_length = l1_connector_distance
    l2_joint_diameter = l1_connector_depth

    l2_joint_size = np.array([
        l2_joint_diameter/2.0,
        l2_joint_length
    ])

    l2_joint_pos = np.array([
        x_offset,
        l1_top-(l2_joint_diameter/2.0),
        z_offset
    ])

    l2_arm_diameter = 0.120 # [m]
    l2_arm_length = 0.245 + (l2_joint_diameter / 2.0) # [m]

    l2_arm_size = np.array([
        l2_arm_diameter/2.0,
        l2_arm_length
    ])

    l2_arm_pos = np.array([
        x_offset,
        l1_top-(l2_joint_diameter/2.0)+(l2_arm_length/2.0),
        z_offset
    ])

    _build_arm_segment(
            xode,
            name='pa10_l2',
            mass=l2_mass,
            passset=pa10_passset,
            joint_size=l2_joint_size,
            joint_pos=l2_joint_pos,
            arm_size=l2_arm_size,
            arm_pos=l2_arm_pos,
            color=dark_gray
    )

    l2_top = l1_top + (l2_arm_length - (l2_joint_diameter / 2.0)) # [m]

    # Determine link 3 parameters
    l3_mass = 3510.0 # [g]

    # Define the l3 base parameters
    l3_base_height = 0.040 # [m]
    l3_base_diameter = l2_arm_diameter

    l3_base_size = np.array([
        l3_base_diameter/2.0,
        l3_base_height
    ])

    l3_base_pos = np.array([
        x_offset,
        l2_top+(l3_base_height/2.0),
        z_offset
    ])
    
    # Define the l3 connectors parameters
    l3_connector_height = 0.190 # [m]
    l3_connector_width = 0.046 # [m]
    l3_connector_depth = 0.120 # [m]

    l3_connector_size = np.array([
        l3_connector_height,
        l3_connector_width,
        l3_connector_depth
    ])

    l3_connector_pos = np.array([
        x_offset,
        l2_top+(l3_connector_height/2.0),
        z_offset
    ])

    l3_connector_distance = 0.120 # [m]

    # Build a 'U' shaped connector joint (all of l1)
    _build_connector_joint(
            xode,
            name='pa10_l3',
            mass=l3_mass,
            passset=pa10_passset,
            connector_size=l3_connector_size,
            connector_pos=l3_connector_pos,
            connector_distance=l3_connector_distance,
            base_size=l3_base_size,
            base_pos=l3_base_pos,
            color=light_gray
    )

    l3_top = l2_top + l3_connector_height

    # Determine link 4 parameters
    l4_mass = 4310.0 # [g]

    l4_joint_length = l3_connector_distance
    l4_joint_diameter = l3_connector_depth

    l4_joint_size = np.array([
        l4_joint_diameter/2.0,
        l4_joint_length
    ])

    l4_joint_pos = np.array([
        x_offset,
        l3_top-(l4_joint_diameter/2.0),
        z_offset
    ])

    l4_arm_diameter = 0.100 # [m]
    l4_arm_length = 0.235 + (l4_joint_diameter / 2.0) # [m]

    l4_arm_size = np.array([
        l4_arm_diameter/2.0,
        l4_arm_length
    ])

    l4_arm_pos = np.array([
        x_offset,
        l3_top-(l4_joint_diameter/2.0)+(l4_arm_length/2.0),
        z_offset
    ])

    _build_arm_segment(
            xode,
            name='pa10_l4',
            mass=l4_mass,
            passset=pa10_passset,
            joint_size=l4_joint_size,
            joint_pos=l4_joint_pos,
            arm_size=l4_arm_size,
            arm_pos=l4_arm_pos,
            color=dark_gray
    )

    l4_top = l3_top + (l4_arm_length - (l4_joint_diameter / 2.0)) # [m]

    # Determine link 5 parameters
    l5_mass = 3450.0 # [g]

    # Define the l5 base parameters
    l5_base_height = 0.010 # [m]
    l5_base_diameter = l4_arm_diameter

    l5_base_size = np.array([
        l5_base_diameter/2.0,
        l5_base_height
    ])

    l5_base_pos = np.array([
        x_offset,
        l4_top+(l5_base_height/2.0),
        z_offset
    ])
    
    # Define the l5 connectors parameters
    l5_connector_height = 0.240 # [m]
    l5_connector_width = 0.030 # [m]
    l5_connector_depth = 0.086 # [m]

    l5_connector_size = np.array([
        l5_connector_height,
        l5_connector_width,
        l5_connector_depth
    ])

    l5_connector_pos = np.array([
        x_offset,
        l4_top+(l5_connector_height/2.0),
        z_offset
    ])

    l5_connector_distance = 0.065 # [m]

    # Build a 'U' shaped connector joint (all of l1)
    _build_connector_joint(
            xode,
            name='pa10_l5',
            mass=l5_mass,
            passset=pa10_passset,
            connector_size=l5_connector_size,
            connector_pos=l5_connector_pos,
            connector_distance=l5_connector_distance,
            base_size=l5_base_size,
            base_pos=l5_base_pos,
            color=light_gray
    )

    l5_top = l4_top + l5_connector_height

    # Determine link 6 parameters
    l6_mass = 1460.0 # [g]

    l6_joint_length = l5_connector_distance
    l6_joint_diameter = l5_connector_depth

    l6_joint_size = np.array([
        l6_joint_diameter/2.0,
        l6_joint_length
    ])

    l6_joint_pos = np.array([
        x_offset,
        l5_top-(l6_joint_diameter/2.0),
        z_offset
    ])

    l6_arm_diameter = 0.063 # [m]
    l6_arm_length = 0.238 # [m]

    l6_arm_size = np.array([
        l6_arm_diameter/2.0,
        l6_arm_length
    ])

    l6_arm_pos = np.array([
        x_offset,
        l5_top-(l6_joint_diameter/2.0)+(l6_arm_length/2.0)-0.158,
        z_offset
    ])

    _build_arm_segment(
            xode,
            name='pa10_l6',
            mass=l6_mass,
            passset=pa10_passset,
            joint_size=l6_joint_size,
            joint_pos=l6_joint_pos,
            arm_size=l6_arm_size,
            arm_pos=l6_arm_pos,
            color=dark_gray
    )

    l6_top = l6_arm_pos[1] + (l6_arm_length / 2.0) # [m]

    # Determine link 7 parameters
    l7_mass = 240.0

    l7_length = 0.005 # [m]
    l7_diameter = l6_arm_diameter # [m]

    l7_size = np.array([
        l7_diameter/2.0,
        l7_length
    ])

    l7_pos = np.array([
        x_offset,
        l6_top+(l7_length/2.0),
        z_offset
    ])

    l7_eul = np.array([90.0, 0.0, 0.0])

    # Generate the l7 segement in the model
    xode.insertBody(
            bname='pa10_l7',
            shape='cylinder',
            size=l7_size,
            density=0.0,
            pos=l7_pos,
            passSet=pa10_passset,
            euler=l7_eul,
            mass=l7_mass,
            color=light_gray
    )

    # TODO: Determine joints between each PA10 link
    #xode.insertJoint('pa10_l0', 'pa10_l1', type='amotor', name='pa10_s1')

    return


def _build_arm_segment(xode, name, mass, passset, joint_size, joint_pos,
        arm_size, arm_pos, color):
    """Build Arm Segment

    Construct a arm segment for the PA10 robotic arm.
    """
    # Determine joint parameters
    joint_name = name
    joint_radius = joint_size[0]
    joint_length = joint_size[1]
    joint_eul = np.array([0.0, 90.0, 0.0])

    # Calculate the volume of the joint section for mass distribution purposes
    joint_volume = np.pi * (joint_radius ** 2) * joint_length

    # Determine arm parameters
    arm_name = name + '_arm'
    arm_radius = arm_size[0]
    arm_length = arm_size[1]
    arm_eul = np.array([90.0, 0.0, 0.0])

    arm_volume = np.pi * (arm_radius ** 2) * arm_length

    total_volume = joint_volume + arm_volume
    
    # Calculate the masses for each part of the segment
    joint_mass = mass * (joint_volume / total_volume)
    arm_mass = mass * (arm_volume / total_volume)

    # Generate the arm segment in the model
    xode.insertBody(
            bname=joint_name,
            shape='cylinder',
            size=joint_size,
            density=0.0,
            pos=joint_pos,
            passSet=passset,
            euler=joint_eul,
            mass=joint_mass,
            color=color
    )

    xode.insertBody(
            bname=arm_name,
            shape='cylinder',
            size=arm_size,
            density=0.0,
            pos=arm_pos,
            passSet=passset,
            euler=arm_eul,
            mass=arm_mass,
            color=color
    )
    
    return


def _build_connector_joint(xode, name, mass, passset, connector_size,
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

    _build_oblong_cylinder(
            xode,
            name=connector1_name,
            mass=connector_mass,
            passset=passset,
            size=connector_size,
            pos=connector1_pos,
            color=color
    )

    # Determine second connector parameters
    connector2_name = name + '_connector2'
    connector2_pos = np.array([
        connector_pos[0]-(connector_distance/2.0)-(connector_size[1]/2.0),
        connector_pos[1],
        connector_pos[2]
    ])

    _build_oblong_cylinder(
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


def _build_oblong_cylinder(xode, name, mass, passset, size, pos, color):
    """Build Oblong Cylinder

    Construct an oblong cylinder body.
    """
    height = size[0]
    width = size[1]
    depth = size[2]

    x = pos[0]
    y = pos[1]
    z = pos[2]

    # Determine internal box parameters
    box_name = name
    box_siz = np.array([depth, height-depth, width])
    box_pos = np.array([x, y, z])
    box_eul = np.array([0.0, 90.0, 0.0])

    # Determine upper cylinder parameters
    up_cyl_name = name + '_cyl1'
    up_cyl_siz = np.array([depth/2.0, width])
    up_cyl_pos = np.array([x, y+(height/2.0)-(depth/2.0), z])
    up_cyl_eul = np.array([0.0, 90.0, 0.0])

    # Determine lower cylinder parameters
    lo_cyl_name = name + '_cyl2'
    lo_cyl_siz = np.array([depth/2.0, width])
    lo_cyl_pos = np.array([x, y-(height/2.0)+(depth/2.0), z])
    lo_cyl_eul = np.array([0.0, 90.0, 0.0])

    # Calculate volumes to determine mass distribution
    cyl_volume = width * ((np.pi * (depth / 2.0) ** 2) / 2.0)
    box_volume = width * (height - depth) * depth
    total_volume = (cyl_volume * 2) + box_volume

    # Calculate mass distribution for each body in the shape
    box_mass = mass * (box_volume / total_volume)
    up_cyl_mass = mass * (cyl_volume / total_volume)
    lo_cyl_mass = mass * (cyl_volume / total_volume)

    # Insert all bodies into the model
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

    # Create fixed joints between bodies
    xode.insertJoint(up_cyl_name, box_name, type='fixed')
    xode.insertJoint(lo_cyl_name, box_name, type='fixed')

    return


if __name__ == '__main__':
    pass
