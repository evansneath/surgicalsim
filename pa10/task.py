__author__ = 'Evan Sneath, evansneath@gmail.com'

from pybrain.rl.environments import EpisodicTask

import numpy as np

# Custom class for miscellaneous functions
import utils


class Pa10Task(EpisodicTask):
    def __init__(self, env):
        EpisodicTask.__init__(self, env)

        # Holds all rewards given in each episode
        self.reward_history = []

        # The current timestep counter
        self.count = 0

        # The number of timesteps in the episode
        self.epiLen = 1500

        # Counts the task resets for incremental learning
        self.incLearn = 0

        # Sensor limit values can be used to normalize the sensors from
        # (low, high) to (-1.0, 1.0) given the low and high values. We want to
        # maintain all units by keeping the results unnormalized for now.
        # Keeping the values of these lists at None skips the normalization.
        self.sensor_limits = None
        self.actor_limits = None

        # Create all attributes for current joint observations
        self.joint_angles = []
        self.joint_velocities = []
        self.joint_acclerations = []

        self.old_joint_velocities = []

        # Create the attribute for current tooltip position (x, y, z) [m]
        self.tooltip_position = []

        # Create all attributes for joint limits
        self.joint_max_angles = []
        self.joint_min_angles = []
        self.joint_max_velocities = []
        self.joint_max_torques = []

        # Call the setter function for the joint limit attributes
        self.set_joint_angle_limits()
        self.set_joint_velocity_limits()
        self.set_joint_torque_limits()

        # Compute the maximum power for each joint
        self.joint_max_powers = self.joint_max_torques * self.joint_max_velocities

        return


    def set_joint_angle_limits(self):
        # PA-10 realistic max/min joint angles [degrees]
        # (Found in PA-10 manual)
        # s1 (rotate): 177
        # s2 (pivot) : 91
        # s3 (rotate): 174
        # e1 (pivot) : 137
        # e2 (rotate): 255
        # w1 (pivot) : 165
        # w2 (rotate): 360

        # Define joint maximum rotation angles
        rotation = 360.0

        # Shoulder joint max angles
        s1_max_angle = 177.0 / rotation
        s2_max_angle = 91.0 / rotation
        s3_max_angle = 45.0 / rotation

        # Elbow joint max angles
        e1_max_angle = 137.0 / rotation
        e2_max_angle = 180.0 / rotation

        # Wrist joint max angles
        w1_max_angle = 150.0 / rotation
        w2_max_angle = 170.0 / rotation

        # Set joint maximum rotation angles [rad]
        self.joint_max_angles = np.array([
            #s1_max_angle,
            s2_max_angle,
            s3_max_angle,
            e1_max_angle,
            #e2_max_angle,
            w1_max_angle,
            #w2_max_angle,
        ]) * 2.0 * np.pi

        # Define minimum rotation angles
        s1_min_angle = -s1_max_angle
        s2_min_angle = 0.0
        s3_min_angle = -s3_max_angle

        e1_min_angle = 0.0
        e2_min_angle = -e2_max_angle

        w1_min_angle = 0.0
        w2_min_angle = -w2_max_angle

        # Set joint mimumum rotation angles [rad]
        self.joint_min_angles = np.array([
            #s1_min_angle,
            s2_min_angle,
            s3_min_angle,
            e1_min_angle,
            #e2_min_angle,
            w1_min_angle,
            #w2_min_angle,
        ]) * 2.0 * np.pi

        return


    def set_joint_velocity_limits(self):
        # Define maximum joint velocities [rad/s]
        #These values can be found in the PA10 user manual for each joint
        s1_max_torque = 1.0
        s2_max_torque = 1.0
        s3_max_torque = 2.0
        e1_max_torque = 2.0
        e2_max_torque = 2.0 * np.pi
        w1_max_torque = 2.0 * np.pi
        w2_max_torque = 2.0 * np.pi

        self.joint_max_velocities = np.array([
            #s1_max_torque,
            s2_max_torque,
            s3_max_torque,
            e1_max_torque,
            #e2_max_torque,
            w1_max_torque,
            #w2_max_torque,
        ])

        return


    def set_joint_torque_limits(self):
        # PA-10 realistic max joint torques
        # s1 (rotate): 5.3
        # s2 (pivot) : 5.3
        # s3 (rotate): 2.0
        # e1 (pivot) : 2.0
        # e2 (rotate): 0.36
        # w1 (pivot) : 0.36
        # w2 (rotate): 0.36

        # The torque values for the joints are normalized from the max torque in the env
        #self.torque_max = 5.3

        torque_s1_rotate_norm = 5.3
        torque_s2_pivot_norm = 5.3

        torque_s3_rotate_norm = 2.0
        torque_e1_pivot_norm = 2.0

        torque_e2_rotate_norm = 0.36
        torque_w1_pivot_norm = 0.36
        torque_w2_rotate_norm = 0.36

        # Set joint max torques
        self.joint_max_torques = np.array([
            #torque_s1_rotate_norm,
            torque_s2_pivot_norm,
            torque_s3_rotate_norm,
            torque_e1_pivot_norm,
            #torque_e2_rotate_norm,
            torque_w1_pivot_norm,
            #w2_max_torque,
        ])

        return


    def getObservation(self):
        sensors = EpisodicTask.getObservation(self)

        # Get the current joint angles [rad]
        # The joint angle values will be between -pi and pi in radians
        self.joint_angles = np.asarray(self.env.getSensorByName('JointSensor'))

        # Get the current joint velocities [rad/s]
        self.joint_velocities = np.asarray(self.env.getSensorByName('JointVelocitySensor'))

        # Set the old joint velocities to 0 if this is the first time step
        if not len(self.old_joint_velocities):
            self.old_joint_velocities = np.zeros_like(self.joint_velocities)

        # Get the current joint accelerations [rad/s^2]
        self.joint_acclerations = (np.absolute(self.joint_velocities -
               self.old_joint_velocities) / self.env.dt)

        # Get the current tooltip position (x, y, z) [m]
        self.tooltip_position = np.asarray(self.env.getSensorByName('tooltipPos'))

        # Observations were made. Set current values as old values
        self.old_joint_velocities = np.copy(self.joint_velocities)

        return sensors


    def action_from_joint_angles(self, action):
        # Change range from (-1.0, 1.0) to (0.0, 1.0)
        action = (action + 1.0) / 2.0

        # Scale the action between low and high joint angles
        action = (action * (self.joint_max_angles - self.joint_min_angles) +
                  self.joint_min_angles)

        # Simple PID controller, convert angular velocities to torques to drive
        # the joints. Since we want an output power, the action must be scaled
        # by the max power of the system. Since power=torque*angular_velocity,
        # We can multiply the maximum powers for each joint to find the desired
        # output power.

        # Tune the PI controller using the Ziegler-Nichols method
        # First define the ultimate gain (K_u) and oscillation perion (T_u)
        action = utils.pid_controller(
                input=action,
                k_u=0.6,
                t_u=0.01,
                e_p=self.joint_angles,             # [rad]
                e_i=self.joint_angles*self.env.dt, # [rad*s]
                e_d=self.joint_velocities,         # [rad/s]
                scale=self.joint_max_torques       # [N*m]
        )

        return action


    def performAction(self, action):
        action = self.action_from_joint_angles(action)

        # Carry out the action based on angular velocities
        EpisodicTask.performAction(self, action)

        return


    def isFinished(self):
        if self.count > self.epiLen:
            print 'FINISHED %d: Out of time' % self.incLearn
            self.res()
            return True

        self.count += 1
        return False


    def res(self):
        self.count = 0
        self.incLearn += 1

        self.reward_history.append(self.getTotalReward())
        print 'REWARD: %f' % self.reward_history[-1]

        return


class Pa10MovementTask(Pa10Task):
    def __init__(self, env):
        Pa10Task.__init__(self, env)

        y_floor = -1.5

        # Define the position of the target to touch (x, y, z) [m]
        self.target_position = np.array([0.6, y_floor+0.5, 0.2])

        return


    def getObservation(self):
        sensors = Pa10Task.getObservation(self)

        # Calculate the straightline distance from the arm to the target [m]
        self.distance_to_target = utils.calc_distance(
                self.tooltip_position,
                self.target_position
        )

        return sensors


    def getReward(self):
        # NOTE: A reward is given at every step in the episode

        # The reward is determined by the distance from the target point and
        # if the arm is actively moving to fix its position
        distance_reward = 1.0 / (self.distance_to_target + 0.001)
        reward = distance_reward / self.epiLen

        return reward
