# SurgicalSim Manual

## Introduction

The purpose of this manual is to provide a resource for both users and developers of the SurgicalSim toolchain.

SurgicalSim is a set of applications developed in order to test the effectiveness of artificial neural networks for use in semi-autonomous telesurgery. The scope of this program explores the training and planning of surgical procedure paths from human-performed path data.

The manual is split into two chapters, each highlighting a single application within the toolchain. TrainingSim is responsible for gathering and formatting human-performed procedure data. NeuralSim is used for artificial neural network training, and subsequently, execution of the artificial neural network generated path.

### Nomenclature and Formatting
Keep in mind that all commands, directory structures, and scripts are in a UNIX-like format. SurgicalSim's native development environment is OSX, though porting to Windows (Cygwin or other shell simulator) shouldn't pose many issues. All directories mentioned assume the SurgicalSim project directory as root directory (`/`).


## TrainingSim

The purpose of the training simulator (or TrainingSim) is to provide a simulation environment with which human operators can perform a test procedure around a test article.

The test article, similar to that of the previously tested test articles, is comprised of a base table and eight markers spaced in a square pattern around the table. Markers also have rotational orientations to guide the operator around the test article.

Data is actively collected, processed, and saved throughout a single run. In order to perform a subsequent run, simply move/rename the generated and restart the program.

### Usage

In order to run the TrainingSim application, first navigate to the `/trainingsim` directory. Execute `run.py` (by typing `python run.py` or simply `./run.py`) with any of the options listed below.

```
usage: run.py [-h] [-v] [-r] [-n] [-o OUTFILE]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         show additional output information at runtime
  -r, --randomize       randomize test article gate position and orientation
  -c, --controller      controller is non-local. ip/port info will be prompted
  -o OUTFILE, --outfile OUTFILE
                        target file for the captured path data
```

### Controller

When the program is started, the viewer window will appear while the program attempts to connect to a hardware controller over a network TCP connection. If the hardware controller is locally hosted and on port 5555, no changes must be made. Otherwise, the `--controller` flag can be set. This will prompt for a controller IP address and port on program start. 

Note that any hardware device can be used as a controller as long as the hardware controller is transmitting the accepted data format at a rate equal to or faster than the simulation framerate (Default: 60 Hz). The specific controller data format to be sent over a TCP connection is as follows in [big-endianness](http://en.wikipedia.org/wiki/Endianness):

| Name                   | Data Type | Size (bytes) | Description                                                      |
| ---------------------- | --------- | ------------ | ---------------------------------------------------------------- |
| On/Off                 | Integer   | 4            | Determines if the controller is transmitting useful data         |
| Buttons                | Integer   | 4            | Used to parse button controls. Each byte corresponds to a button |
| Position (_x_)         | Double    | 8            | Position in meters                                               |
| Position (_y_)         | Double    | 8            | Position in meters                                               |
| Position (_z_)         | Double    | 8            | Position in meters                                               |
| Rotation (_α_)         | Double    | 8            | Euler rotation angle in radians                                  |
| Rotation (_β_)         | Double    | 8            | Euler rotation angle in radians                                  |
| Rotation (_γ_)         | Double    | 8            | Euler rotation angle in radians                                  |
| Time Difference (_dt_) | Double    | 8            | Time difference between last and current data transmission       |

A mouse controller for OSX is shipped with this version of SurgicalSim. The controller is located in `tests/phantomomni` and can be run by executing `python mouse_tcp_sim.py` or `./mouse_tcp_sim.py`.

### Defined Procedure

After a controller connection is made, the simulation will begein. The operator may then use the controller to navigate the end effector through the defined procedure. By default, the procedure starts at the right-center marker, goes clockwise around the test article through all other markers, and ends back at the right-center marker.

The defined procedure can be changed if needed by modifying the test article constants such as `G_GATE_NORM_POS`, `G_GATE_POS`, `G_GATE_HEIGHT`, or `G_GATE_NORM_ROT` in `/lib/constants.py`.

### Simulation Controls

During the simulation, several actions can be taken to manipulate the camera position and control the simulation.

Standard movement of the controller with no buttons pressed will manipulate the end effector. This is used once camera controls are set to appropriate positions so that the operator can effectively move the end effector around the test article.

The simulation camera operates in a [spherical coordinate system](http://en.wikipedia.org/wiki/Spherical_coordinate). Meaning that the camera moves spherically around the center point of the simulation. Two buttons (the first two bits of the 'Buttons' controller data) are used to initate camera controls. If the first bit (button 1) is pressed, any movement modifies the polar and azimuth angles based on the given _x_ and _z_ coordinates. The second bit (button 2) enters zoom mode. When button 2 is held, any increase/decrease in the controller _z_ coordinate proportionally increases/decreases the radius, _r_, of the camera from the center point. Note that movements of the controller position/rotation during camera adjustment *does* manipulate the end effector. For this reason, it is best to set the camera before beginning the procedure.

The following useful keyboard controls were also implemented.

| Key | Action                                                |
| --- | ----------------------------------------------------- |
| `q` | Quits the viewer application and stops the simulation |
| `c` | Resets the camera to the initial position             |
| `f` | Enters fullscreen mode                                |
| `s` | Captures a screenshot                                 |

After the procedure is performed, the user may stop the simulation by pressing `q` in the viewer window. At this point, path data formatting begins.

### Procedure Path Trimming and Rating

Trimming and rating are necessary tasks to ensure useful data for artificial neural network training. Both processes are automatically performed as soon as the simulation is stopped. Helpful graphical user interfaces guide the operator through each process.

Trimming is the process of removing extraneous path data before and after the desired procedure path. Two sliders on the graphical interface control the amount of the path trimmed from the start (top slider) and end (bottom slider) of the procedure. The user should attempt to trim such that the procedure starts and ends as close to the single start/end marker as possible. Click the 'Trim' button when finished.

The rating interface will appear after trimming. The rating interface highlights the segment of path between markers for examination. A rating is on a scale of 1 (Unable to perform) to 5 (Performs easily with good flow). This rating scale is based on a [mastoidectomy assessment tool](http://www.ncbi.nlm.nih.gov/pubmed/19885831). Once a suitable rating has been determined, the evaluator can enter the determined rating in the command line prompt. The interface will record the rating and advance to the next segment until all segments have been rated.

### Data Output

The path data, once processed, is saved to the default of `out.dat` in the `/trainingsim` directory or the file given with the `--output` flag.

The data present in this file is a [NumPy array](http://docs.scipy.org/doc/numpy/reference/generated/numpy.array.html) with size of NxM (N being the number of time steps recorded, and M being the number of parameters per time step). The arrays can be programmatically saved and loaded using the respective [numpy.save](http://docs.scipy.org/doc/numpy/reference/generated/numpy.save.html) and [numpy.load](http://docs.scipy.org/doc/numpy/reference/generated/numpy.load.html) functions. The path parameters saved for each time step are listed in the table below:

| Name                           | Data Type   | Units   | Description                                             |
| ------------------------------ | ----------- | ------- | ------------------------------------------------------- |
| Time                           | Double      | Seconds | Current time of the data point from start               |
| Gate Position/Orientation (x8) | Double (x4) | Meters  | The _x_, _y_, _z_, _θ_ for each gate in procedure order |
| End Effector Position          | Double (x3) | Meters  | The _x_, _y_, _z_ position of the end effector          |
| Rating                         | Double      | N/A     | The normalized rating (0.0 to 1.0) of the current step  |

The data should be stored in the `/data` directory in the SurgicalSim root for easy neural network training.


## NeuralSim

The purpose of the neural network simulator (or NeuralSim) is to provide a method for easy training of path planning neural networks and playback of the generated path. As expected, this is performed in two distinct steps; neural network training, and generated path playback/correction.

### Usage
In order to run the NeuralgSim application, first navigate to the `/neuralsim` directory. Execute `run.py` (by typing `python run.py` or simply `./run.py`) with any of the options listed below.

```
usage: run.py [-h] [-v] [-r] [-f] [-n NETWORK]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         show additional output information at runtime
  -r, --randomize       randomize test article gate placement
  -f, --fast            use fast simulation steps (for slower machines)
  -n NETWORK, --network NETWORK
                        load neural network parameters from xml file
```

### Neural Network Training

In order to generate a path from the data collected in TrainingSim, the artificial neural network must first be trained until error convergence. Once many (4-5) training data sets are collected and placed in the `/data` directory, the NeuralSim application can be started. Upon starting, NeuralSim will automatically use the training datasets placed in the `/data` directory to train the artificial neural network. Constants such as the training data directory, maximum number of training iterations, and error convergence thresholds can be modified if needed in `/lib/constants.py`.

After convergence is acheived or the maximum number of training iterations is reached, the trained artificial neural network will be saved to `trained-rnn.xml` in the `/neuralsim` directory. Saving of the neural network is performed by the PyBrain NetworkWriter module. This module allows any PyBrain neural network along with trained weights to be saved in an XML formatted file.

If the `--network` option flag is set and a PyBrain network XML file is given, the neural network will be loaded from that file and used for immediate path generation. This is very useful if a neural network has already been successfully trained and only path generation is desired.

**Note: Training may take several hours**

### Neural Network Generation and Playback

After neural network training, the trained neural network will generate a path around the test article from an independant input dataset. The number of time steps to generate can be controlled using the `G_RNN_GENERATED_TIME_STEPS` constants in `/lib/constants.py`. Generation takes milliseconds to complete.

Playback occurs directly after path generation. The simulation viewer window will appear and remain paused for 10 seconds. After the pause time elapses, the generated path will be played back. Any dynamic movements in marker position during the course of the simulation will be corrected by the real-time path correction algorithm.

An oscillation of the test article can be imposed or turned off by the `G_TABLE_IS_OSCILLATING` constant. The `G_TABLE_OSCILLATION_AMP` and `G_TABLE_OSCILLATION_FREQ` constants (in `/lib/constants.py`) may also be tuned to test the path correction algorithm during the simulation.

Both the statically generated path and the path performed with the path correction algorithm are outputted at the end of the simulation. The static path is saved to `static-path.dat`, and the dynamic path is saved to `dynamic-path.dat` in the `/neuralsim` directory. These path names can be changed if desired by modifying the `G_RNN_STATIC_PATH_OUT` and `G_RNN_DYNAMIC_PATH_OUT` constants in `/lib/constants.py`.


## PathUtils

The Path Utilities (or PathUtils) program, located at `/lib/pathutils.py`, was developed to simplify and abstract the actions of displaying and manipulating the custom `.dat` format. Though many of the functions of this program are performed automatically during the main TrainingSim-NeuralSim toolchain, the path plotting functionality of PathUtils prove to be most necessary; therefore, the primary subject of this section is path plotting.

### Usage

In order to run the NeuralgSim application, first navigate to the `/lib` directory. Execute `pathutils.py` (by typing `python pathutils.py` or simply `./pathutils.py`) with any of the options listed below.

```
usage: pathutils.py [-h] [-t] [-n] [-f] [-i TITLE] [-o OUT] paths [paths ...]

positional arguments:
  paths                 file(s) containing path data

optional arguments:
  -h, --help            show this help message and exit
  -t, --trim            trim the start and end of the path
  -n, --normalize       normalize path time
  -f, --fix             modify the initial position of the path
  -i TITLE, --title TITLE
                        specify output plot title
  -o OUT, --out OUT     alternate path output
```

### Plotting

The PathUtils program accepts one or many plots in the command line interface. The first path filename specified in the command line will plot as a solid blue line while all other path filenames will plot as a dashed red line. This is important for distinguishing between two or more paths at the same time.

The title of the plot may also be modified by the operator if desired. This is done using the `--title` flag followed by the desired plot title surrounded by parentheses.

The generated plot can be scaled, resized, zoomed, or rotated to fit the users needs. After manipulation is finished, the plot may be saved to disk using the save button located on the bottom of the window. The plot can be closed using the standard window close button specific to the host operating system.
