# Manual
The purpose of this manual is to provide a resource for both users and developers of the SurgicalSim toolchain.

SurgicalSim is a set of applications developed in order to test the effectiveness of artificial neural networks for use in semi-autonomous telesurgery. The scope of this program explores the training and planning of surgical procedure paths from human-performed path data.

The manual is split into two chapters, each highlighting a single application within the toolchain. TrainingSim is responsible for gathering and formatting human-performed procedure data. NeuralSim is used for artificial neural network training, and subsequently, execution of the artificial neural network generated path.

### Nomenclature and Formatting
Keep in mind that all commands, directory structures, and scripts are in a UNIX-like format. SurgicalSim's native development environment is OSX, though porting to Windows shouldn't pose many issues. All directories mentioned assume the SurgicalSim project directory as root directory.

## TrainingSim
### Usage
In order to run the TrainingSim application, first navigate to the `/trainingsim` directory. Execute `run.py` (by typing `python run.py` or simply `./run.py`) with any of the options listed below.

```
usage: run.py [-h] [-v] [-r] [-n] [-o OUTFILE]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         show additional output information at runtime
  -r, --randomize       randomize test article gate placement
  -n, --network         controller is non-local. ip/port info will be prompted
  -o OUTFILE, --outfile OUTFILE
                        target path for the tooltip pickled data
```

## NeuralSim
### Usage
In order to run the NeuralgSim application, first navigate to the `/neuralsim` directory. Execute `run.py` (by typing `python run.py` or simply `./run.py`) with any of the options listed below.

```
usage: run.py [-h] [-v] [-r] [-f] [-n NETWORK]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         show additional output information at runtime
  -r, --randomize       randomize test article gate placement
  -f, --fast            use fast step function (for slower machines)
  -n NETWORK, --network NETWORK
                        load neural network parameters from xml file
```
