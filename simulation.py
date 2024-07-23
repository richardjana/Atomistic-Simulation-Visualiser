import time
from math import pi, sin, cos
from random import randrange
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence
# Change this panda3d.core import to be more specific
from panda3d.core import *
from lammps import lammps
import numpy as np


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Create lammps object and get initial coords
        self.lmp = lammps()
        self.lmp.file("read_from_file.in")
        self.coords = self.lmp.numpy.extract_atom("x")

        self.atom_count = self.lmp.get_natoms()
        self.atoms = []
        self.atom_ids = self.lmp.numpy.extract_atom("id")
        # delayTime determines how long each timestep takes
        self.delayTime = 1

        # Add templates for different atoms. Add more or change values depending on amount of atoms in simulation
        self.atom_types = {1: {"color": [0.9, 0.9, 0.9], "scale": [0.1, 0.1, 0.1]},
                           2: {"color": [0.9, 0.0, 0.0], "scale": [0.15, 0.15, 0.15]}}
        self.atom_type_list = self.lmp.numpy.extract_atom("type")

        # Create pointlight to make atom details visible
        plight1 = PointLight('plight1')
        plight1.setColor((0.7, 0.7, 0.7, 1))
        plnp1 = self.render.attachNewNode(plight1)
        plnp1.setPos(100, 100, 100)
        self.render.setLight(plnp1)

        # Create second pointlight to make the "dark side" brighter
        plight2 = PointLight('plight2')
        plight2.setColor((0.7, 0.7, 0.7, 1))
        plnp2 = self.render.attachNewNode(plight2)
        plnp2.setPos(-100, -100, -100)
        self.render.setLight(plnp2)

        # Create ambientlight to make things more visible
        alight = AmbientLight('alight')
        alight.setColor((0.4, 0.4, 0.4, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        print("Creating atoms...")
        # Add the createAtomsTask to task manager
        self.taskMgr.add(self.createAtomsTask, "CreateAtomsTask")

        # Add the moveAtomsTask to task manager
        self.taskMgr.add(self.moveAtomsTask, "MoveAtomsTask")

        # print("Setting up the camera...")
        # Add the spinCameraTask to task manager
        # self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")



    def createAtomsTask(self, task):
        for atom_id in self.atom_ids:
            # Load atom model. If simulation has a lot of atoms or needs to run very quickly,
            # change the model to a lower poly version, which can be found online. Any .egg file should work.
            atom = self.loader.loadModel('Sphere_HighPoly.egg')
            # Reparent to render (important to do this so the model can be rendered)'
            atom.reparentTo(self.render)
            if self.atom_type_list[atom_id - 1] in self.atom_types.keys():
                atom.setColor(self.atom_types[self.atom_type_list[atom_id - 1]]["color"][0],
                              self.atom_types[self.atom_type_list[atom_id - 1]]["color"][1],
                              self.atom_types[self.atom_type_list[atom_id - 1]]["color"][2], 1)
                atom.setScale(self.atom_types[self.atom_type_list[atom_id - 1]]["scale"][0],
                              self.atom_types[self.atom_type_list[atom_id - 1]]["scale"][1],
                              self.atom_types[self.atom_type_list[atom_id - 1]]["scale"][2])
            # Give atoms random positions
            atom.setPos(self.coords[atom_id - 1][0], self.coords[atom_id - 1][1], self.coords[atom_id - 1][2])
            # Add atoms to a list, so they can be easily accessed later
            self.atoms.append(atom)
        return Task.done



    def moveAtomsTask(self, task):
        starttime = time.monotonic()
        self.run_single()
        # Give the atoms random movement that changes every self.delayTime seconds

        # Using and not using IDs seem to result in same outcome
        """
        for atom_id in self.atom_ids:
            atom = self.atoms[atom_id - 1]
            # Get old position and get random new position
            old_pos = atom.getPos()
            new_pos = [self.coords[atom_id - 1][0], self.coords[atom_id - 1][1], self.coords[atom_id - 1][2]]
            # Set posInterval that changes the location of the atom to a new one over
            # the course of self.delayTime seconds
            posInterval = atom.posInterval(self.delayTime, Point3(new_pos[0], new_pos[1], new_pos[2]),
                                           Point3(old_pos[0], old_pos[1], old_pos[2]))
            posInterval.start()
        """
        for i in range(self.atom_count):
            atom = self.atoms[i]
            old_pos = atom.getPos()
            new_pos = [self.coords[i][0], self.coords[i][1], self.coords[i][2]]
            posInterval = atom.posInterval(self.delayTime, Point3(new_pos[0], new_pos[1], new_pos[2]),
                                           Point3(old_pos[0], old_pos[1], old_pos[2]))
            posInterval.start()
        self.taskMgr.doMethodLater(self.delayTime - (time.monotonic() - starttime), self.moveAtomsTask, "MoveAtomsTask")
        return Task.done



    def run_single(self):
        # Run single timestep and get ids and coords of atoms
        self.lmp.command("run 1")
        self.atom_ids = self.lmp.numpy.extract_atom("id")
        self.coords = self.lmp.numpy.extract_atom("x")
        f = open("test.txt", "a")
        for atom_id in self.atom_ids:
            f.write(f"{atom_id}, {self.lmp.map_atom(1)}, x, y, z: {self.coords[atom_id - 1][0]}, {self.coords[atom_id - 1][1]}, {self.coords[atom_id - 1][2]}\n")


"""
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * pi / 180.0
        self.camera.setPos(30 * sin(angleRadians), -30 * cos(angleRadians), 0)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont
"""



if __name__ == "__main__":
    app = MyApp()
    app.run()