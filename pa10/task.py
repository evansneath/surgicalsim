__author__ = 'Evan Sneath, evansneath@gmail.com'

from pybrain.rl.environments import EpisodicTask

import numpy as np


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

        # Create all attributes for joint limits
        self.joint_max_angles = []
        self.joint_min_angles = []
        self.joint_max_velocities = []
        self.joint_max_torques = []

        # Call the setter function for the joint limit attributes
        self.set_joint_angle_limits()
        self.set_joint_velocity_limits()
        self.set_joint_torque_limits()

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
        w1_max_angle = 165.0 / rotation
        w2_max_angle = 180.0 / rotation

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


    def performAction(self, action):
        # Get joint angles and speeds

        # The joint angle values will be between -pi and pi in radians
        joint_angles = np.asarray(self.env.getSensorByName('JointSensor'))
        joint_velocities = np.asarray(self.env.getSensorByName('JointVelocitySensor'))

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
        action = (np.tanh(action - joint_angles - joint_velocities *
                          self.joint_max_torques) *
                  self.joint_max_torques * self.joint_max_velocities)

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

        # Set the current and old tooltip position attributes
        self.tooltip_pos = np.asarray(self.env.getSensorByName('tooltipPos'))
        self.old_tooltip_pos = np.asarray(self.env.getSensorByName('tooltipPos'))
        self.tooltip_start = np.asarray(self.env.getSensorByName('tooltipPos'))

        # Define velocity and acceleration values
        self.velocity = 0.0
        self.old_velocity = 0.0

        self.acceleration = 0.0

        # Define the position of the target to hit
        self.target_pos = np.array([0.6, y_floor+0.5, 0.2])

        # Initialize distance between the tooltip and target
        self.distance_to_target = self.calc_distance(
                self.tooltip_pos,
                self.target_pos
        )

        self.smoothness_total = 0.0

        return

    def calc_distance(self, source, destination):
        """Calculate Distance

        Calculate the distance between any two points in the environment.

        Arguments:
            source: The start point.
            destination: The target point.
        """
        return np.sqrt(((source - destination) ** 2).sum())

    def getObservation(self):
        # Collect data about the world at each moment

        # Get the current tooltip location [m]
        self.tooltip_pos = np.asarray(self.env.getSensorByName('tooltipPos'))

        # Calculate the straightline distance from the arm to the target point [m]
        self.distance_to_target = self.calc_distance(
                self.tooltip_pos,
                self.target_pos
        )

        # Calculate the distance of the tooltip from the previous moment [m]
        pos_difference = self.calc_distance(
                self.tooltip_pos,
                self.old_tooltip_pos
        )
        
        # Calculate the velocity for this moment [m/s]
        self.velocity = pos_difference / self.env.dt

        # Calculate the acceleration of this moment [m/s^2]
        self.acceleration = np.absolute(self.velocity - self.old_velocity)

        # Set the values of this moment as "old" values
        self.old_velocity = self.velocity
        self.old_tooltip_pos = self.tooltip_pos

        sensors = Pa10Task.getObservation(self)

        return sensors

    def print_point_debug(self):
        # Just print out information of the location of everything
        print ('Tooltip is at: (x=%f, y=%f, z=%f)' %
               (self.tooltip_pos[0], self.tooltip_pos[1], self.tooltip_pos[2]))
        print ('Target is at: (x=%f, y=%f, z=%f)' %
               (self.target_pos[0], self.target_pos[1], self.target_pos[2]))
        print 'Distance to target is %f m' % self.distance
        print 'Velocity is %f m/s' % self.velocity

        return

    def isFinished(self):
        # If we hit the point, we're done here
        # TODO: Uncomment this when an incentive is given to hit the target
        #if self.distance <= 0.04 and not self.reached_target:
        #    print 'Reached target at time %d/%d' % (self.count, self.epiLen)
        #    self.res()
        #    return True

        # Perform the normal time-check to determine if we are done
        result = Pa10Task.isFinished(self)

        return result

    def getReward(self):
        # NOTE: A reward is given at every point in time in the episode

        # The reward is determined by the distance from the target point and
        # if the arm is actively moving to fix its position
        distance_reward = 1.0 / (self.distance_to_target + 0.001)

        # Reward a low amount of acceleration for each moment
        #smoothness_reward = 1.0 / (self.acceleration + 1.0)

        reward = distance_reward / self.epiLen

        return reward
