#!/bin/bash

# 0 ---------- SETUP ----------
cd ~

# Change this as needed. Directory in ~ where install will take place
INSTALL_DIR=Workspace

# This is the directory where you Python dist packages are installed
DIST_PACKAGES_DIR=/usr/local/lib/python2.7/dist-packages

# Create the install directory if it doesn't exist and move there
mkdir ${INSTALL_DIR}
INSTALL_DIR=~/${INSTALL_DIR}
cd ${INSTALL_DIR}

# 1 ---------- INSTALL UTILITIES ----------

# 1.1 Install development utilities
sudo apt-get -y install git vim-gnome

# 1.2 Install Python utility packages
sudo apt-get -y install python-setuptools cython


# 2 ---------- INSTALL PYTHON PACKAGES ----------

# 2.1 Install Python scientific packages (NumPy, SciPy, MatPlotLib)
sudo apt-get -y install python-numpy python-scipy python-matplotlib

# 2.2 Install ODE and ODE Python bindings
# (Download ODE from SourceForge)
sudo curl -L -O http://downloads.sourceforge.net/project/opende/ODE/0.13/ode-0.13.tar.gz
# (Extract ODE tarfile)
tar -xvf ode-0.13.tar.gz
cd ${INSTALL_DIR}/ode-0.13
# (Configure and build ODE)
sudo ./configure --enable-double-precision --with-trimesh=opcode --enable-new-trimesh --enable-shared
sudo make
sudo make install
# (Install Python bindings)
cd ${INSTALL_DIR}/ode-0.13/bindings/python
sudo python setup.py install
# (Move back to base dir)
cd ${INSTALL_DIR}
# (Cleaning up)
sudo rm -fr ode-0.13*

# 2.3 Install Python OpenGL bindings
sudo apt-get -y install python-opengl

# 2.4 Install PyODE (deprecated library) for XODE modules
# (Check out the repo)
git clone http://git.code.sf.net/p/pyode/git pyode-git
# (Move only the XODE module into the Python dist-packages dir)
sudo cp -R ${INSTALL_DIR}/pyode-git/xode ${DIST_PACKAGES_DIR}
# (Clean up, we no longer need this)
sudo rm -fr ${INSTALL_DIR}/pyode-git


# 3 ---------- INSTALL CUSTOM PROJECTS (PYBRAIN/SURGICALSIM) ----------

# 3.1 Clone all project repos
git clone http://github.com/evansneath/pybrain
git clone http://github.com/evansneath/surgicalsim

# 3.2 Install custom PyBrain package
cd ${INSTALL_DIR}/pybrain
sudo python setup.py install
# (Copy XODE changes from PyBrain into XODE install)
sudo cp ./pybrain/rl/environments/ode/xode_changes/* ${DIST_PACKAGES_DIR}/xode/
cd ${INSTALL_DIR}

# 3.3 Install the surgicalsim package (by creating a symbolic link)
sudo ln -s ${INSTALL_DIR}/surgicalsim ${DIST_PACKAGES_DIR}/surgicalsim

echo "Done."
