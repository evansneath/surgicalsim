__author__ = 'Evan Sneath, evansneath@gmail.com'

from pybrain.rl.environments import EpisodicTask
from pybrain.rl.environments.ode.sensors import SpecificBodyPositionSensor
from scipy import tanh, array, sqrt, absolute, pi


class Pa10Task(EpisodicTask):
    def __init__(self, env):
        EpisodicTask.__init__(self, env)

        # Take the defined max torque from the Pa10Environment as max power

        # Power = Torque * Angular_Velocity
        self.maxPower = self.env.torque_max * 2.0 * pi

        # Holds all rewards given in each episode
        self.reward_history = []

        # The current timestep counter
        self.count = 0

        # The number of timesteps in the episode
        self.epiLen = 1500

        # Counts the task resets for incremental learning
        self.incLearn = 0

        # Environment coefficient of friction
        self.env.FricMu = 20.0 # 8.0

        # Real-world time for each time step
        self.env.dt = 0.005

        # Add all actuators to the sensor limits
        self.sensor_limits = []
        self.actor_limits = None

        # Set angle sensor limits
        for i in range(self.env.actLen):
            self.sensor_limits.append((self.env.cLowList[i], self.env.cHighList[i]))

        # Set joint velocity sensor limits
        for i in range(self.env.actLen):
            self.sensor_limits.append((-2.0 * pi, 2.0 * pi))

        # Add the PA-10 tooltip position sensor
        self.env.addSensor(SpecificBodyPositionSensor(['pa10_t2'], 'tooltipPos'))

        # Update the number of sensors
        self.env.obsLen = self.env.outdim

        old_act_num = self.env.actLen
        self.env.actLen = self.env.indim

        # Add the sensor limits of the tooltip sensor to the list (3 dimensions)
        for i in range(3):
            self.sensor_limits.append((-4, 4))
        
        return

    def performAction(self, action):
        # Get joint angles and speeds
        joints = array(self.env.getSensorByName('JointSensor'))
        speeds = array(self.env.getSensorByName('JointVelocitySensor'))

        #if self.count % self.epiLen == 500:
        #    print 'JOINTS:', joints
        #    print 'SPEEDS:', speeds
        #    print 'ACTION:', action
        #    print 'HIGH LIMIT:', self.env.cHighList, type(self.env.cHighList)
        #    print 'LOW LIMIT:', self.env.cLowList, type(self.env.cLowList)
        #    print 'TORQUES:', self.env.torqueList, type(self.env.torqueList)
        #    print 'MAX TORQUE:', self.maxPower, type(self.maxPower)

        # Convert all torques to anglular speeds
        #act = ((action + 1.0) / 2.0 * (self.env.cHighList -
        #          self.env.cLowList) + self.env.cLowList)
        #action = (tanh((act - joints - 0.9 * speeds * self.env.torqueList) *
        #          16.0) * self.maxPower * self.env.torqueList)

        # Since the PA10 has joint velocity limits, these must be enforced in
        # the output joint velocity action. Max velocity is determined to this
        # point by Power * Torque, so in order to proportionally reduce the
        # angular velocity, the current velocity must be multiplied by these
        # scaling values

        max_angle_velocities = array([
            1.0 / (2.0 * pi), # S2 max = 1.0 [rad/s]
            1.0 / pi,         # S3 max = 2.0 [rad/s]
            1.0 / pi,         # E1 max = 2.0 [rad/s]
            1.0,              # W1 max = 2.0 * pi [rad/s]
        ])

        # Change range from (-1.0, 1.0) to (0.0, 1.0)
        action = (action + 1.0) / 2.0

        # Scale the action between low and high joint angles
        action = (action * (self.env.cHighList - self.env.cLowList) +
                self.env.cLowList)

        # Simple PID controller, convert torques to angular velocities
        action = (tanh(action - joints - speeds * self.env.torqueList) *
                  self.maxPower * self.env.torqueList * max_angle_velocities)

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
        self.tooltip_pos = array(self.env.getSensorByName('tooltipPos'))
        self.old_tooltip_pos = array(self.env.getSensorByName('tooltipPos'))
        self.tooltip_start = array(self.env.getSensorByName('tooltipPos'))

        # Define velocity and acceleration values
        self.velocity = 0.0
        self.old_velocity = 0.0

        self.acceleration = 0.0

        # Define the position of the target to hit
        self.target_pos = array([0.6, y_floor+0.5, 0.2])

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
        return sqrt(((source - destination) ** 2).sum())

    def getObservation(self):
        # Collect data about the world at each moment

        # Get the current tooltip location [m]
        self.tooltip_pos = array(self.env.getSensorByName('tooltipPos'))

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
        self.acceleration = absolute(self.velocity - self.old_velocity)

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
