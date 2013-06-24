__author__ = 'Evan Sneath, evansneath@gmail.com'

from pybrain.rl.environments import EpisodicTask
from pybrain.rl.environments.ode.sensors import SpecificBodyPositionSensor
from scipy import tanh, array, sqrt, absolute


class Pa10Task(EpisodicTask):
    def __init__(self, env):
        EpisodicTask.__init__(self, env)

        # Take the defined max torque from the Pa10Environment as max power
        self.maxPower = self.env.torque_max
        print 'MAX TORQUE: %f' % self.maxPower

        # Holds all rewards given in each episode
        self.reward_history = []

        # The current timestep counter
        self.count = 0

        # The number of timesteps in the episode
        self.epiLen = 1000

        # Counts the task resets for incremental learning
        self.incLearn = 0

        # Environment coefficient of friction
        self.env.FricMu = 20.0

        # Real-world time for each time step
        self.env.dt = 0.01#0.0008

        # Add all actuators to the sensor limits
        self.sensor_limits = []
        self.actor_limits = None

        # Set angle sensor limits
        for i in range(self.env.actLen):
            self.sensor_limits.append((self.env.cLowList[i], self.env.cHighList[i]))

        # Set joint velocity sensor limits
        for i in range(self.env.actLen):
            self.sensor_limits.append((-20, 20))

        # Add the PA-10 tooltip position sensor
        self.env.addSensor(SpecificBodyPositionSensor(['pa10_t1'], 'tooltipPos'))

        # Update the number of sensors
        self.env.obsLen = self.env.outdim
        self.env.actLen = self.env.indim

        # Add the sensor limits of this sensor to the list (3 dimensions)
        for i in range(3):
            self.sensor_limits.append((-4, 4))

        return

    def performAction(self, action):
        # Get joint angles and speeds
        joints = array(self.env.getSensorByName('JointSensor'))
        speeds = array(self.env.getSensorByName('JointVelocitySensor'))

        #if self.count % self.epiLen == 0:
        #    print 'JOINTS:', joints, type(joints)
        #    print 'SPEEDS:', speeds, type(speeds)

        #    print 'ACTION:', action, type(action)
        #    print 'HIGH LIMIT:', self.env.cHighList, type(self.env.cHighList)
        #    print 'LOW LIMIT:', self.env.cLowList, type(self.env.cLowList)
        #    print 'TORQUES:', self.env.torqueList, type(self.env.torqueList)
        #    print 'MAX TORQUE:', self.maxPower, type(self.maxPower)

        # Convert all torques to anglular speeds
        act = ((action + 1.0) / 2.0 * (self.env.cHighList -
                  self.env.cLowList) + self.env.cLowList)
        action = (tanh((act - joints - 0.9 * speeds * self.env.torqueList) *
                  16.0) * self.maxPower * self.env.torqueList)

        #if self.count % self.epiLen == 0:
        #    print 'NEW ACTION:', action, type(action)

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

        # Define the position of the target to hit
        self.target_pos = array([1.0, 1.0, 0.0])

        # Initialize distance between the tooltip and target
        self.distance = 0.

        return

    def getObservation(self):
        # Collect data about the world at each step

        # Get the current tooltip location
        self.tooltip_pos = array(self.env.getSensorByName('tooltipPos'))

        # Calculate the straightline distance from the arm to the target point
        self.distance = sqrt(((self.tooltip_pos - self.target_pos) ** 2).sum())

        self.difference = sqrt(((self.tooltip_pos - self.old_tooltip_pos) ** 2).sum())
        self.velocity = self.difference / self.env.dt

        self.old_tooltip_pos = self.tooltip_pos

        sensors = Pa10Task.getObservation(self)

        # Print out some debug stuff every time we run an episode
        if self.count % self.epiLen == 0:
            self.printDebug()
        #    print 'TOOLTIP:', self.tooltip_pos
        #    print 'SENSOR NAMES:', self.env.getSensorNames()
        #    print 'SENSOR VALUES:', sensors

        return sensors

    def printDebug(self):
        # Just print out information of the location of everything
        print ('Tooltip is at: (x=%f, y=%f, z=%f)' %
               (self.tooltip_pos[0], self.tooltip_pos[1], self.tooltip_pos[2]))
        print ('Target is at: (x=%f, y=%f, z=%f)' %
               (self.target_pos[0], self.target_pos[1], self.target_pos[2]))
        print 'Difference is %f meters' % self.distance
        print 'Velocity is %f m/s' % self.velocity

        return

    def isFinished(self):
        # If we hit the point, we're done here
        if self.distance == 0.:
            print 'FINISHED %d: Reached target' % self.incLearn
            self.res()
            return True

        # Perform the normal time-check to determine if we are done
        result = Pa10Task.isFinished(self)

        return result

    def getReward(self):
        # The reward is determined by the distance from the target point and
        # if the arm is actively moving to fix its position
        reward = (1 / (self.distance + 0.1)) / self.epiLen
        return reward
