__author__ = 'Evan Sneath, evansneath@gmail.com'

from pybrain.rl.environments import EpisodicTask
from pybrain.rl.environments.ode.sensors import SpecificBodyPositionSensor
from scipy import tanh, array, sqrt

class Pa10Task(EpisodicTask):
    def __init__(self, env):
        EpisodicTask.__init__(self, env)

        # Take the defined max torque from the Pa10Environment as max power
        self.maxPower = env.torque_max

        # Holds all rewards given in each episode
        self.reward_history = []

        # The current timestep counter
        self.count = 0

        # The number of timesteps in the episode
        self.epiLen = 700

        # Counts the task resets for incremental learning
        self.incLearn = 0

        # Environment coefficient of friction
        self.env.FricMu = 20.0

        # Real-world time for each time step
        self.env.dt = 0.01

        # Add all actuators to the sensor limits
        self.sensor_limits = []
        self.actor_limits = []

        # Angle sensors and actuator limits
        for i in range(self.env.actLen):
            self.sensor_limits.append((self.env.cLowList[i], self.env.cHighList[i]))
            self.actor_limits.append((self.env.cLowList[i], self.env.cHighList[i]))
            #self.actor_limits.append((-1, 1))

        # Joint velocity sensors
        for i in range(self.env.actLen):
            self.sensor_limits.append((-20, 20))

        # Add the PA-10 tooltip position sensor
        self.env.addSensor(SpecificBodyPositionSensor(['pa10_t1'], 'tooltipPos'))

        # Update the number of sensors
        self.env.obsLen = self.env.outdim

        # Add the sensor limits of this sensor to the list
        for i in range(self.env.obsLen - 2 * self.env.actLen):
            self.sensor_limits.append((-4, 4))

        return

    def performAction(self, action):
        # Get joint angles and speeds
        joints = array(self.env.getSensorByName('JointSensor'))
        speeds = array(self.env.getSensorByName('JointVelocitySensor'))

        #print 'JOINTS:', joints, type(joints)
        #print 'SPEEDS:', speeds, type(speeds)

        #print 'ACTION:', action, type(action)
        #print 'HIGH LIMIT:', self.env.cHighList, type(self.env.cHighList)
        #print 'LOW LIMIT:', self.env.cLowList, type(self.env.cLowList)
        #print 'TORQUES:', self.env.torqueList, type(self.env.torqueList)
        #print 'MAX TORQUE:', self.maxPower, type(self.maxPower)

        # Convert all torques to anglular speeds
        action = ((action + 1.0) / 2.0 * (self.env.cHighList -
                  self.env.cLowList) + self.env.cLowList)
        action = (tanh((action - joints - 0.9 * speeds * self.env.torqueList) *
                  16.0) * self.maxPower * self.env.torqueList)

        #print 'NEW ACTION:', action, type(action)

        EpisodicTask.performAction(self, action)

        return

    def isFinished(self):
        if self.count > self.epiLen:
            self.res()
            return True

        self.count += 1
        return False

    def res(self):
        self.count = 0
        self.incLearn += 1

        self.reward_history.append(self.getTotalReward())

        return


class MovementTask(Pa10Task):
    def __init__(self, env):
        Pa10Task.__init__(self, env)

        self.tooltip = array([0., 0., 0.])
        self.distance = array([0., 0., 0.])
        self.target = array([0.5, 0.5, 0.])

        return

    def getObservation(self):
        # Collect data about the world at each step

        # Get the current tooltip location
        self.tooltip = self.env.getSensorByName('tooltipPos')
        #y_floor = -1.5
        #self.tooltip[1] -= y_floor

        # Calculate the difference for each dimension
        difference = self.tooltip - self.target

        # Calculate the straightline distance from the arm to the target point
        self.distance = sqrt((difference[0:3] ** 2).sum())

        # Print a debug statement each time the observation is run
        self.printDebug()

        sensors = Pa10Task.getObservation(self)

        #print 'TOOLTIP:', self.tooltip
        #print 'SENSOR NAMES:', self.env.getSensorNames()
        #print 'SENSOR VALUES:', sensors

        return sensors

    def printDebug(self):
        # Just print out information of the location of everything
        print ('Tooltip is at: (x=%f, y=%f, z=%f)' %
               (self.tooltip[0], self.tooltip[1], self.tooltip[2]))
        print ('Target is at: (x=%f, y=%f, z=%f)' %
               (self.target[0], self.target[1], self.target[2]))
        print 'Difference is %f meters' % self.distance

        return

    def isFinished(self):
        # If we hit the point, we're done here
        if self.distance == 0.:
            self.res()
            return True

        # Perform the normal time-check to determine if we are done
        Pa10Task.isFinished(self)

        return

    def getReward(self):
        # The reward is determined by the distance from the point and bonus is
        # given for less time taken to acheive the task
        reward = (1 / (self.distance + 0.1)) / float(self.count)

        return reward
