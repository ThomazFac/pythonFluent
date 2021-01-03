#!/usr/bin/env python3
"""
Classes of the Ansys Fluent Python Wrapper to generate Ansys Fluent input files
for faster setup, command-line usage and parametrization.
"""

import sys
import os
from pathlib import Path
import json


class Simulation:
    """
    Ansys Fluent simulation class for generating, controlling and postprocessing Fluent cases.
    Create objects (or in this context called simulations) and setup your simulation using this class methods,
    such as the turbulence model, file input / output, discretization, boundary conditions, etc.

    Full documentation can be found here :      https://www.github.com
    """
    def __init__(self, dimension, workingDir=None):
        self._workingDir = workingDir
        self.dimensions = ['2d-planar', '2d-axisymmetric', '2d-axisymmetric-swirl', '3d']
        if isinstance(dimension, str):
            if dimension not in self.dimensions:
                print("\nError dimension in Simulation(dimension). \nAllowed dimensions: \'2d-planar\', \'2d-axisymmetric\', \'2d-axisymmetric-swirl\', \'3d\'")
                sys.exit()
            if dimension == '2d-planar':
                self._dimension = 'fluent 2ddp'
            elif dimension == '2d-axisymmetric':
                self._dimension = 'fluent 2ddp'
            elif dimension == '2d-axisymmetric':
                self._dimension = 'fluent 2ddp'
            elif dimension == '3d':
                self._dimension = 'fluent 3ddp'
        else:
            print("\nError in simulation declaration, \'dimension\' must be of type 'str'. Allowed dimensions: \'2d-planar\', \'2d-axisymmetric\', \'2d-axisymmetric-swirl\', \'3d\'")

        self._case = None
        self._import = None
        self._readMesh = None
        self._readCase = None
        self._readData = None
        self._time = None
        self._solver = None
        self._energy = None
        self._turbulenceModel = None
        self._boundaryConditions = None
        self._materials = None
        self._writeCase = None


    def readMesh(self, mesh, path=os.getcwd()):
        """
        Read Fluent mesh file in the format of ".msh" (ascii or binary)

        ----------
        Parameters
        ----------

        #1 mesh     :   mesh name of ".msh" file. If no path is given, the directory where the Python file will be executed will be set as the path.
                        It is recommended to always provide the absolute path.
        """

        tempString = ""

        if not path.endswith("/"):
            path += "/"

        if not mesh.endswith(".msh"):
            mesh += ".msh"

        if not os.path.exists(path):
            print("Provided path in \'readMesh(mesh, path)\'doesn't exist, please provide valid directory")
            sys.exit()

        tempString += "\n/file/read-mesh {}".format(path + mesh)
        self._mesh = tempString


    def readCase(self, case, path=os.getcwd()):
        """
        Read Fluent case file in the format of ".cas" or ".cas.h5" into Fluent

        ----------
        Parameters
        ----------

        #1 case     :   Casename or -path to the ".cas" or ".cas.h5" file. If no path is given, the directory where the Python file will be executed will be set as the path.
                        It is recommended to always provide the absolute path.
        """

        tempString = ""

        if not path.endswith("/"):
            path += "/"

        if not case.endswith(".cas"):
            if not case.endswith(".h5"):
                case += ".cas"

        if not os.path.exists(path):
            print("Provided path in \'readCase(mesh, path)\'doesn't exist, please provide valid directory")
            sys.exit()

        tempString += "\n/file/read-case {}".format(case + path)
        self._case = tempString


    def time(self, time):
        """
        @type time: str

        Set the type of time-formulation for the simulation.

        ----------
        Parameters
        ----------

        #1 time     :   steady-state    (RANS simulations)
                        transient       (URANS and LES simulations)
        """

        tempString = ""

        if time == "steady-state":
            tempString += """/define models steady? yes"""
        elif time == "transient":
            tempString += """/define unsteady-1st-order? yes"""
        else:
            print("\nYou entered an invalid parameter for the time-formulation in \'Simulation.time(time)\'. Available time parameters: \'steady-state\', \'transient\'")
            sys.exit()

        self._time = tempString


    def solver(self, solver: str, *args, **kwargs):
        """
        Set the type and algorithm of the solver for the simulation.

        ----------
        Parameters
        ----------

        #1 solver       :   pressure-based
                            density-based

        #2 scheme       :   simple, simplec, piso, coupled  (for 'pressure-based' solver only)


        #3 formulation  :   explicit, implicit              (for 'density-based' solver only)

        #4 fluxType     :   ausm, roe                       (for 'density-based' solver only)

        """

        tempString = ""

        # pbSchemes       = ['simple', 'simplec', 'piso', 'coupled']
        # dbFormulations  = ['implicit', 'explicit']
        # dbFluxTypes     = ['roe-fds', 'ausm']

        solver = '-'.join(solver.split()).lower()

        args = ['-'.join(i.split()).lower() for i in args]  # Clean args list

        if solver == 'pressure-based':
            tempString += """\n/define/models/solver/pressure-based"""
            if 0 < len('args') < 2:
                scheme = args[0]
                if scheme == "simple":
                    tempString += """\n/solve/set/p-v-coupling 20"""
                elif scheme == "simplec":
                    tempString += """\n/solve/set/p-v-coupling 21"""
                elif scheme == "piso":
                    tempString += """\n/solve/set/p-v-coupling 22"""
                elif scheme == "coupled":
                    tempString += """\n/solve/set/p-v-coupling 24"""
                else:
                    print("\nYou entered an invalid scheme for the pressure-based solver in \'Simulation.solver(type, scheme, formulation, fluxType)\'. Available schemes: \'simple\', \'simplec\', \'piso\', \'coupled\'")
                    sys.exit()

        elif solver == 'density-based':
            tempString += """\ndefine/models/solver/density-based-implicit yes"""
            if 0 < len(args) < 3:  # Check if density based solver args are given (implicit, roe-fds, ...)
                arg1 = args[0]
                if len(args) > 1:  # If 2 args are given
                    arg2 = args[1]
                    if arg1 == 'implicit':
                        pass  # has already been defined
                    elif arg1 == 'explicit':
                        tempString = """\ndefine/models/solver/density-based-explicit yes"""
                    else:
                        print("\nYou entered an invalid formulation for the density-based solver in \'Simulation.solver(type, formulation, fluxType)\'. Available formulations: \'implicit\', \'explicit\'")
                        sys.exit()
                    if arg2 == 'roe-fds':
                        tempString += """\n/solve/set/flux-type 0"""
                    elif arg2 == 'ausm':
                        tempString += """\n/solve/set/flux-type 1"""
                    else:
                        print("\nYou entered invalid flux-type for the density-based solver in \'Simulation.solver(solver, formulation, fluxType)\'. Available flux-types: \'roe-fds\', \'ausm\'")
                        sys.exit()

                # If only one arg is given
                if 0 < len(args) < 2:
                    if arg1 == 'implicit':
                        pass  # has already been defined
                    elif arg1 == 'explicit':
                        tempString = """\ndefine/models/solver/density-based-explicit yes"""
                    else:
                        print("\nYou entered an invalid formulation for the density-based solver in \'Simulation.solver(type, formulation, fluxType)\'. Available formulations: \'implicit\', \'explicit\'")
                        sys.exit()

        # If wrong solver is given
        else:
            print("\nhello, You entered an invalid solver in \'Simulation.solver(type, algorithm, fluxType)\'. Available solvers: \'pressure-based\', \'density-based\'")
            sys.exit()

        self._solver = tempString


    def turbulenceModel(self, model, type, options=None, wallFunction="standard", shieldingFunction="iddes"):
        """
        @type model: str
        @type type: str
        @type options: list
        @type wallFunction: str
        @type shieldingFunction: str

        Set the turbulence model of your simulation. Note that for steady-state problems only RANS turbulence models are allowed while
        for transient simulations you may use URANS or DES / LES models.

        ----------
        Parameters
        ----------

        #1 model         :   spalart-allmaras, k-epsilon, k-omega, transition-sst, v2-f, reynolds-stress, SAS, DES, LES

        #2 options (list):   spalart-allmaras :   type           =  vorticity-based, strain-vorticity-based
                                                  options        =  viscous-heating

                             k-epsilon        :   type           =  standard, rng, realizable, rg-easm
                                                  wall-functions =  standard, scalable, non-equilibrium, enhanced, menter-lechner
                                                  options        =  differential-viscosity-model, viscous-heating, compressibility-effects, production-kato-launder, production-limiter

                             k-omega          :   type           =  standard, bsl, sst, geko, rg-easm
                                                  options        =  shear-flow-corrections, low-re-corrections, viscous-heating, compressibility-effects, production-kato-launder, production-limiter, intermittency-transition-model

                             transition-sst   :   options        =  viscous-heating, production-kato-launder, production-limiter

                             v2-f             :   options        =  viscous-heating, compressibility-effects

                             reynolds-stress  :   type           =  linear-pressure-strain, quadratic-pressure-strain, stress-omega, stress-bsl
                                                  options        =  wall-bc-from-k-equation, wall-reflection-effects, viscous-heating, compressibility-effects, low-re-corrections, shear-flow-corrections, geko
                                                  wall-functions =  standard, scalable, non-equilibrium, enhanced

                             SAS              :   options        =  viscous-heating, compressibility-effects, production-kato-launder, production-limiter, intermittency-transition-model

                             DES              :   rans-model     =  spalart-allmaras, realizable-k-epsilon, sst-k-omega
                                                  options        =  low-re-corrections, delayed-des, viscous-heating, production-kato-launder, production-limiter, intermittency-transition-model
                                                  shielding-functions = sst-f1, sst-f2, ddes, iddes

                             LES              :   type           =  smagorinsky-lilly, wale, wmles, wmles-s-omega, kinetic-energy-transport
                                                  options        =  dynamic-stress, viscous-heating, dynamic-energy-flux
        """

        if options is None:
            options = []

        tempString: str = ""

        # Turbulence models
        turbulenceModels = { "spalart-allmaras"  : { "types"    :   ["vorticity-based", "strain-vorticity-based"],
                                                     "options"  :   ["viscous-heating"] },

                             "k-epsilon"         : { "types"    :   ["standard", "rng", "realizable", "rg-easm"],
                                                     "options"  :   ["differential-viscosity-model", "viscous-heating", "compressibility-effects", "production-kato-launder", "production-limiter" ],
                                                     "wall-functions" : ["standard", "scalable", "non-equilibrium", "enhanced", "menter-lechner"] },

                             "k-omega"           : { "types"    :   ["standard", "bsl", "sst", "geko", "rg-easm"],
                                                     "options"  :   ["shear-flow-corrections", "low-re-corrections", "viscous-heating", "compressibility-effects", "production-kato-launder", "production-limiter", "intermittency-transition-model"] },

                             "transition-sst"    : { "options"  :   ["viscous-heating", "production-kato-launder", "production-limiter", "roughness-correlation" ] },

                             "v2-f"              : { "options"  :   ["viscous-heating", "compressibility-effects"] },

                             "rsm"               : { "types"    :   ["linear-pressure-strain", "quadratic-pressure-strain", "stress-omega", "stress-bsl"],
                                                     "options"  :   ["wall-bc-from-k-equation", "wall-reflection-effects", "viscous-heating", "compressibility-effects", "low-re-corrections", "shear-flow-corrections", "geko"],
                                                     "wall-functions" : ["standard", "scalable", "non-equilibrium", "enhanced", "menter-lechner"] },

                             "sas"               : { "options"  :   ["viscous-heating", "compressibility-effects", "production-kato-launder", "production-limiter", "intermittency-transition-model"] },

                             "des"               : { "types"    :   ["spalart-allmaras", "realizable-k-epsilon", "sst-k-omega"],
                                                     "options"  :   ["low-re-corrections", "delayed-des", "viscous-heating", "production-kato-launder", "production-limiter", "intermittency-transition-model"],
                                                     "shielding-functions" : ["sst-f1", "sst-f2", "ddes", "iddes"] },

                             "les"               : { "types"    :   ["smagorinsky", "wale", "wmles", "wmles-s-omega", "kinetic-energy-transport"],
                                                     "options"  :   ["dynamic-stress", "viscous-heating", "dynamic-energy-flux"] }
                             }


        # Clean-up strings
        model, type, wallFunction, shieldingFunction = '-'.join(model.split()).lower(), '-'.join(type.split()).lower(), '-'.join(wallFunction.split()).lower(), '-'.join(shieldingFunction.split()).lower()

        if len(options) > 0:
            for i, option in enumerate(options):
                options[i] = '-'.join(options[i].split()).lower()

        # Check if turbulence model was correctly set
        if model not in turbulenceModels:
            print("\nInvalid turbulence model, allowed models: \"spalart-allmaras, k-epsilon, k-omega, transition-sst, v2-f, reynolds-stress, SAS, DES, LES\"")
            sys.exit()

        # Model
        # ----------------
        # Spalart-allmaras
        # ----------------
        if model == "spalart-allmaras":
            tempString += "\n/define/models/viscous/spalart-allmaras yes"
            if type is None and type not in turbulenceModels["spalart-allmaras"]["types"]:
                print("\nInvalid spalart-allmaras type, allowed types: \"vorticity-based, strain-vorticity-based\"")
                sys.exit()

            # Type
            if type == "vorticity-based":
                tempString += "\n/define/models/viscous/sa-alternate-prod no"
            elif type == "strain-vorticity-based":
                tempString += "\n/define/models/viscous/sa-alternate-prod yes"
            else:
                print("\nInvalid spalart-allmaras type, allowed types: \"vorticity-based, strain-vorticity-based\"")
                sys.exit()

            # Options
            if len(options) > 0:
                if "viscous-heating" in options:
                    tempString += "\n/define/models/energy yes yes yes"
                    options.remove("viscous-heating")
                if len(options) > 0:
                    print("\nInvalid options in the spalart-allmaras model, allowed options: \"viscous-heating\"")
                    sys.exit()

        # ---------
        # k-epsilon
        # ---------
        elif model == "k-epsilon":
            if type != None and type not in turbulenceModels["k-epsilon"]["types"]:
                print("\nInvalid k-epsilon model type, allowed types: \"standard, rng, realizable, rg-easm\"")
                sys.exit()

            # Type
            if type == "standard":
                tempString += "\n/define/models/viscous/ke-standard yes"
            elif type == "rng":
                tempString += "\n/define/models/viscous/ke-rng yes"
            elif type == "realizable":
                tempString += "\n/define/models/viscous/ke-realizable yes"
            elif type == "rg-easm":
                tempString += "\n(allow-easm-model)\n/define/models/viscous/ke-easm yes"

            # Options
            if len(options) > 0:
                if "viscous-heating" in options:
                    tempString += "\n/define/models/energy yes yes yes"
                    options.remove("viscous-heating")
                if "compressibility-effects" in options:
                    tempString += "\n/define/models/viscous/turb-compressibility yes"
                    options.remove("compressibility-effects")
                if type == "rng":
                    if "differential-viscosity-model" in options:
                        tempString += "\n/define/models/viscous/rng-difff yes"
                        options.remove("differential-viscosity-model")
                if "production-kato-launder" in options:
                    tempString += "\n/define/models/viscous/turbulence-expert/kato-launder-model yes"
                    options.remove("production-kato-launder")
                if "production-limiter" in options:
                    tempString += "\n/define/models/viscous/turbulence-expert/production-limiter yes 10"
                    options.remove("production-limiter")
                if len(options) > 0:
                    print("\nInvalid options in the k-epsilon model, allowed options: \"differential-viscosity-model", "viscous-heating", "compressibility-effects", "production-kato-launder", "production-limiter\"")
                    sys.exit()

            # Wall-functions
            if wallFunction is not None and wallFunction in turbulenceModels["k-epsilon"]["wall-functions"]:
                if wallFunction == "standard":
                    pass
                elif wallFunction == "scalable":
                    tempString += "\n/define/models/viscous/near-wall-treatment/scalable yes"
                elif wallFunction == "non-equilibrium":
                    tempString += "\n/define/models/viscous/near-wall-treatment/non-equi yes"
                elif wallFunction == "enhanced":
                    tempString += "\n/define/models/viscous/near-wall-treatment/enhanced yes"
                elif wallFunction == "menter-lechner":
                    tempString += "\n/define/models/viscous/near-wall-treatment/menter yes"
            else:
                print("\nInvalid wall-function in the k-epsilon-model, allowed wall-functions: \"standard", "scalable", "non-equilibrium", "enhanced", "menter-lechner\"")

        # -------
        # k-omega
        # -------
        elif model == "k-omega":
            if type is None and type not in turbulenceModels["k-omega"]["types"]:
                print("\nInvalid k-omega model type, allowed types: \"standard, bsl, sst, rg-easm, geko\"")
                sys.exit()

            # Type
            if type == "standard":
                tempString += "\n/define/models/viscous/kw-standard yes"
            elif type == "bsl":
                tempString += "\n/define/models/viscous/kw-bsl yes"
            elif type == "sst":
                tempString += "\n/define/models/viscous/kw-sst yes"
            elif type == "rg-easm":
                tempString += "\n(allow-easm-model)\n/define/models/viscous/kw-rg-easm yes"
            elif type == "geko":
                tempString += "\n/define/models/viscous/kw-geko yes"

            # Options
            if len(options) > 0:
                if "viscous-heating" in options:
                    tempString += "\n/define/models/energy yes yes yes"
                    options.remove("viscous-heating")
                if "compressibility-effects" in options:
                    tempString += "\n/define/models/viscous/turb-compressibility yes"
                    options.remove("compressibility-effects")
                if "production-kato-launder" in options:
                    tempString += "\n/define/models/viscous/turbulence-expert/kato-launder-model yes"
                    options.remove("production-kato-launder")
                if "production-limiter" in options:
                    tempString += "\n/define/models/viscous/turbulence-expert/production-limiter yes 10"
                    options.remove("production-limiter")
                if "shear-flow-corrections" in options:
                    tempString += "\n/define/models/viscous/kw-shear yes"
                    options.remove("shear-flow-corrections")
                if "low-re-corrections" in options:
                    tempString += "\n/define/models/viscous/kw-low-re yes"
                    options.remove("low-re-corrections")
                if type == "bsl" or type == "sst":
                    if "intermittency-transition-model" in options:
                        tempString += "\n/define/models/viscous/add-inter yes yes"
                        options.remove("intermittency-transition-model")
                if len(options) > 0:
                    print("\nInvalid options in the k-omega model, allowed options: \'viscous-heating\', \'compressibility-effects\', \'production-kato-launder\', \'production-limiter\', \'intermittency-transition-model\', \'low-re-corrections\'")
                    sys.exit()


        # --------------------------------
        # transition-SST or gamma-re-theta
        # --------------------------------
        elif model == ("transition-sst" or "gamma-re-theta"):

            tempString += "\n/define/models/viscous/transition yes"

            # Options
            if len(options) > 0:
                if "viscous-heating" in options:
                    tempString += "\n/define/models/energy yes yes yes"
                    options.remove("viscous-heating")
                if "production-kato-launder" in options:
                    tempString += "\n/define/models/viscous/turbulence-expert/kato-launder-model yes"
                    options.remove("production-kato-launder")
                if "production-limiter" in options:
                    tempString += "\n/define/models/viscous/turbulence-expert/production-limiter yes 10"
                    options.remove("production-limiter")
                if "roughness-correlation" in options:
                    tempString += "\n/define/models/viscous/turbulence-expert/production-limiter yes 10"
                    options.remove("roughness-correlation")
                if len(options) > 0:
                    print("\nInvalid options in the transition-SST model, allowed options: \'viscous-heating\', \'production-kato-launder\', \'production-limiter\', \'roughness-correlation\'")
                    sys.exit()


        # --------------------------------
        # v2-f
        # --------------------------------
        elif model == "v2-f":

            tempString += "\n(allow-v2f-model)\n/define/models/viscous/v2f yes"

            # Options
            if len(options) > 0:
                if "viscous-heating" in options:
                    tempString += "\n/define/models/energy yes yes yes"
                    options.remove("viscous-heating")
                if "compressibility-effects" in options:
                    tempString += "\n/define/models/viscous/turb-compressibility yes"
                    options.remove("compressibility-effects")
                if len(options) > 0:
                    print("\nInvalid options in the v2-f model, allowed options: \'viscous-heating\', \'compressibility-effects\'")
                    sys.exit()


        # ---------------
        # reynolds-stress
        # ---------------
        elif model == ("reynolds-stress-model" or "rsm"):
            if type is not None and type not in turbulenceModels["rsm"]["types"]:
                print("\nInvalid reynolds-stress model type, allowed types: \"linear-pressure-strain\", \"quadratic-pressure-strain\", \"stress-omega\", \"stress-bsl\"")
                sys.exit()

            # Type
            if type == "linear-pressure-strain":
                tempString += "\n/define/models/viscous/reynolds yes\n/define/models/viscous/rsm-linear yes"
            elif type == "quadratic-pressure-strain":
                tempString += "\n/define/models/viscous/reynolds yes\n/define/models/viscous/rsm-ssg yes"
            elif type == "stress-omega":
                tempString += "\n/define/models/viscous/reynolds yes\n/define/models/viscous/rsm-omega yes"
            elif type == "stress-bsl":
                tempString += "\n/define/models/viscous/reynolds yes\n/define/models/viscous/rsm-bsl yes"

            # Options
            if len(options) > 0:
                if "viscous-heating" in options:
                    tempString += "\n/define/models/energy yes yes yes"
                    options.remove("viscous-heating")
                if "compressibility-effects" in options:
                    tempString += "\n/define/models/viscous/turb-compressibility yes"
                    options.remove("compressibility-effects")
                # if "wall-bc-from-k-equation" in options:
                #     tempString += "\n/define/models/viscous/turb-compressibility yes"
                #     options.remove("differential-viscosity-model")
                if type == ("linear-pressure-strain" or "quadratic-pressure-strain"):
                    if "wall-reflection-effects" in options:
                        tempString += "\n/define/models/viscous/rsm-wall-echo yes"
                        options.remove("wall-reflection-effects")
                if type == ("stress-omega" or "stress-bsl"):
                    if "low-re-corrections" in options:
                        tempString += "\n/define/models/viscous/kw-low-re yes"
                        options.remove("low-re-corrections")
                    if "shear-flow-corrections" in options:
                        tempString += "\n/define/models/viscous/kw-shear yes"
                        options.remove("shear-flow-corrections")
                if type == "stress-bsl":
                    if "geko" in options:
                        tempString += "\n/define/models/viscous/rsm-or-earsm-geko yes"
                        options.remove("geko")
                if len(options) > 0:
                    print("\nInvalid options in the reynolds-stress model, allowed options: \"wall-bc-from-k-equation\", \"wall-reflection-effects\", \"viscous-heating\", \"compressibility-effects\", \"low-re-corrections\", \"shear-flow-corrections\", \"geko\"")
                    sys.exit()

            # Wall-functions
            if type == ("linear-pressure-strain" or "quadratic-pressure-strain"):
                if wallFunction in turbulenceModels["rsm"]["wall-functions"]:
                    if wallFunction == "standard":
                        pass
                    elif wallFunction == "scalable":
                        tempString += "\n/define/models/viscous/near-wall-treatment/scalable yes"
                    elif wallFunction == "non-equilibrium":
                        tempString += "\n/define/models/viscous/near-wall-treatment/non-equiv yes"
                    if type == "linear-pressure-strain":
                        if wallFunction == "enhanced":
                            tempString += "\n/define/models/viscous/near-wall-treatment/enhanced yes"
                else:
                    print("\nInvalid wall-function in the reynolds-stress-model, allowed wall-functions: \'standard\', \'scalable\', \'non-equilibrium\', \'enhanced (only linear-pressure-strain)\'")


        # --------------------------------
        # sas
        # --------------------------------
        elif model == "sas":

            if self._time == """/define models steady? yes""":
                print("\nSAS model only available for transient simulations. Please change Simulation.time(\"steady-state\") to Simulation.time(\"transient\")")
                sys.exit()

            # Options
            if len(options) > 0:
                if "viscous-heating" in options:
                    tempString += "\n/define/models/energy yes yes yes"
                    options.remove("viscous-heating")
                if "compressibility-effects" in options:
                    tempString += "\n/define/models/viscous/turb-compressibility yes"
                    options.remove("compressibility-effects")
                if "productions-kato-launder" in options:
                    tempString += "\n/define/models/viscous/turbulence-expert/kato-launder-model yes"
                    options.remove("productions-kato-launder")
                if "production-limiter" in options:
                    tempString += "\n/define/models/viscous/turbulence-expert/production-limiter yes 10"
                    options.remove("production-limiter")
                if "intermittency-transition-model" in options:
                    tempString += "\n/define/models/viscous/add-inter yes yes"
                    options.remove("intermittency-transition-model")
                if len(options) > 0:
                    print("\nInvalid options in the sas model, allowed options: \'viscous-heating\', \'compressibility-effects\', \'production-kato-launder\', \'production-limiter\', \'intermittency-transition-model\'")
                    sys.exit()


        # ---------------
        # des
        # ---------------
        elif model == "des":

            if self._time == """/define models steady? yes""":
                print("\nDES model only available for transient simulations. Please change Simulation.time(\"steady-state\") to Simulation.time(\"transient\")")
                sys.exit()

            if type is not None and type not in turbulenceModels["des"]["types"]:
                print("\nInvalid DES model type, allowed types: \"spalart-allmaras\", \"realizable-k-epsilon\", \"sst-k-omega\"")
                sys.exit()

            # Type
            if type == "spalart-allmaras":
                tempString += "\n/define/models/viscous/ke-standard yes"
            elif type == "quadratic-pressure-strain":
                tempString += "\n/define/models/viscous/ke-rng yes"
            elif type == "realizable-k-epsilon":
                tempString += "\n/define/models/viscous/ke-realizable yes"
            elif type == "sst-k-omega":
                tempString += "\n(allow-easm-model)\n/define/models/viscous/ke-easm yes"

            # Options
            if len(options) > 0:
                if "viscous-heating" in options:
                    tempString += "\n/define/models/energy yes yes yes"
                    options.remove("viscous-heating")
                if "delayed-des" in options:
                    tempString += "\n/define/models/viscous/turb-compressibility yes"
                    options.remove("delayed-des")
                if "production-kato-launder" in options:
                    tempString += "\n/define/models/viscous/turbulence-expert/kato-launder-model yes"
                    options.remove("production-kato-launder")
                if "production-limiter" in options:
                    tempString += "\n/define/models/viscous/turbulence-expert/production-limiter yes 10"
                    options.remove("production-limiter")
                if "low-re-corrections" in options:
                    tempString += "\n/define/models/viscous/kw-low-re yes"
                    options.remove("production-limiter")
                if "intermittency-transition-model" in options:
                    tempString += "\n/define/models/viscous/add-inter yes yes"
                    options.remove("intermittency-transition-model")
                if len(options) > 0:
                    print("\nInvalid options in the DES model, allowed options: \"low-re-corrections\", \"delayed-des\", \"viscous-heating\", \"production-kato-launder\", \"production-limiter\", \"intermittency-transition-model\"")
                    sys.exit()

            # Shielding-functions
            if shieldingFunction in turbulenceModels["des"]["shielding-functions"]:
                if shieldingFunction == "sst-f1":
                    tempString += "\n/define/models/viscous/        "
                elif shieldingFunction == "sst-f2":
                    tempString += "\n/define/models/viscous/        "
                elif shieldingFunction == "ddes":
                    tempString += "\n/define/models/viscous/        "
                elif shieldingFunction == "iddes":
                    tempString += "\n/define/models/viscous/        "
            else:
                print('\nInvalid shielding-function in the DES model, allowed shielding-functions: \'sst-f1\', \'sst-f2\', \'ddes\', \'iddes\'')
                sys.exit()


        # ---------------
        # les
        # ---------------
        elif model == "les":

            if self._time == """/define models steady? yes""":
                print("\nLES model only available for transient simulations. Please change Simulation.time(\"steady-state\") to Simulation.time(\"transient\")")
                sys.exit()

            if type is not None and type not in turbulenceModels["les"]["types"]:
                print('\nInvalid LES model type, allowed types: \'smagorinsky\', \'wale\', \'wmles\', \'wmles-s-omega\', \'kinetic-energy-transport\'')
                sys.exit()

            tempString += "\n/define/models/viscous/large yes"

            # Type
            if type == "smagorinsky":
                if "dynamic-stress" in options:
                    tempString += "\n/define/models/viscous/les-subgrid-smag yes yes"
                else:
                    tempString += "\n/define/models/viscous/les-subgrid-smag yes no"
                if "dynamic-energy-flux" in options:
                    tempString += "\n/define/models/viscous/les-dynamic yes"
            elif type == "wale":
                tempString += "\n/define/models/viscous/les-subgrid-wale yes"
            elif type == "wmles":
                tempString += "\n/define/models/viscous/les-subgrid-wmles yes"
            elif type == "wmles-s-omega":
                tempString += "\n/define/models/viscous/les-subgrid-wmles-s yes"
            elif type == "kinetic-energy-transport":
                tempString += "\n/define/models/viscous/les-subgrid-tke yes"
                if "dynamic-energy-flux" in options:
                    tempString += "\n/define/models/viscous/les-dynamic yes"

            # Options
            if len(options) > 0:
                if "viscous-heating" in options:
                    tempString += "\n/define/models/energy yes yes yes"
                    options.remove("viscous-heating")
                if len(options) > 0:
                    print('\nInvalid options in the LES model, allowed options: \'dynamic-stress\', \'fviscous-heating\', \'dynamic-energy-flux\'')
                    sys.exit()


    def materials(self, material=["air", "fluid"], *args, **kwargs):
        """
        Create or modify materials (fluids or solids) to be used in your computational domain.

        ----------
        Parameters
        ----------

        Properties in labeled with "*" are optional. It is recommended to use the default values from the database.
        #1 material :   str OR list; if str: name or chemical formula (lowercase), elif list: (name or chemical formula (lowercase), state)
        #2 state    :   str; state = ["solid", "fluid", "inert-particle", "droplet", "combusting-particle"]
        #3 density  :   list; [type, *properties]     type        = [ 'constant', 'incompressible-ideal-gas', 'ideal-gas', 'power-law',
                                                                      'real-gas-aungier-redlich-kwong', 'real-gas-sutherland']
                                                      *properties = { 'constant': float,
                                                                      'incompressible-ideal-gas': ['property1': float},
                                                                      'ideal-gas',
                                                                      'p
        #4 viscosity:   list; [type, *properties]     type        = [ 'constant', 'incompressible-ideal-gas', 'ideal-gas', 'power-law',
                                                                      'real-gas-aungier-redlich-kwong', 'real-gas-sutherland']
                                                      *properties = { 'constant': float,
                                                                      'incompressible-ideal-gas': ['property1': float},
                                                                      'ideal-gas',
                                                                      'powerlaw': [ (x1, x2, x3,...], [y1, y2, y3, ...] ],
                                                                      'piecewise-polynomial': { [T1, T2], (x1, x2, x3, ...), (y1, y2, y3, ...),
                                                                                                [T2, T3], (x1, x2, x3, ...), (y1, y2, y3, ...) },
                                                                      'piecewise-linear':


        Example for an incompressible fluid with DEFAULT parameters:
        materials('air', density='constant')

        Example for a compressible fluid with DEFAULT parameters:
        materials('n2', 'ideal-gas')

        Example for a compressible fluid with customized parameters:
        materials('n2', 'ideal-gas', viscosity='sutherland', specificHeat=520.64, thermalConductivity=0.024)

        A list of all materials can be found in the file: 'db/matdb.json'
        """

        tempString = ""
        matDict = {}  # Initialize material dict for later generation of Fluent string (will be called only once)

        # Dict of default properties
        defaultProperties = { 'density': ["constant", 1.225], 'viscosity': ["constant", 1.7894e-5], 'specificHeat': ["constant", 1006.43],
                              'thermalConductivity': ["constant", 0.0242], 'molecularWeight': ["constant", 28.966], 'lennardJonesLength': ["constant", 3.711],
                              'lennardJonesEnergy': ["constant", 78.6], 'thermalAccomCoefficient': ["constant", 0.9137], 'velocityAccomCoefficient': ["constant", 0.9137],
                              'formationEntropy': ["constant", 194336], 'criticalPressure': ["constant", 3.758e6], 'criticalTemperature': ["constant", 132.2],
                              'acentricFactor': ["constant", 0.033], 'criticalVolume': ["constant", 0.002857]}

        # Check if fluid state was given and not throw an error if second argument is density
        if isinstance(material, str):
            pass
        elif isinstance(material, list):
            material = material[0]
            try:
                state = material[1]
                state = '-'.join(state.split()).lower()
            except:
                pass
        else:
            print("\nYou passed the wrong function argument when calling the material method. \nAllowed material argument: str or list.\nE.g. material(\"air\") or material([\"air\", \"fluid\"])")
            sys.exit()

        material = '-'.join(material.split()).lower()

        # Import materials database
        with open("../db/matdb.json", "r") as f:
            db = json.load(f)

        # Check if name or chemical formula was given correctly
        try:
            mat = db[material]
        except:
            try:
                for key, value in db.items():
                    if value['chemicalFormula'] == material:
                        mat = key
            except:
                print("\nInvalid name or chemical formula given. Check db/material.json for a list of materials.")
                sys.exit()

        # Check if args list is empty
        # if len(args) > 0:
        #     for i, j in enumerate(args):
        #         if i == 0:  # Density
        #             tempString += """\n/define/material"""

        for key, value in kwargs.items():
            key = '-'.join(key.split()).lower()
            if key == "density":
                if isinstance(value, str) or isinstance(value, float) or isinstance(value, int):
                    try:
                        value = float(value)
                        tempString += """\ndefine/material/air de"""
                elif isinstance(value, list):
                    densityType, value = value[0], value[1]
                else:
                    pass


    def boundaryConditions(self):
        """
        Set the boundary conditions of your simulation.
        """
        def velocityInlet(self, name, components=[0,0,0], normalToBoundary=0, staticPressure=0, turbulenceIntensity=5, turbulentViscosityRatio=10, staticTemperature=300):
            if self._energy == False:  # incompressible case
                pass
            elif self._energy == True:  # compressible case
                pass
            else:
                print("\nInvalid energy formulation")
                sys.exit()
        def massflowInlet(self, name, components=[0,0,0], normalToBoundary=0, massFlux=0, staticPressure=0, turbulenceIntensity=5, turbulentViscosityRatio=10, staticTemperature=300):
            pass
        def pressureFarfield(self, name, components=[0,0,0], staticPressure=0, turbulenceIntensity=5, turbulentViscosityRatio=10, staticTemperature=300):
            if self._energy == False:  # incompressible case
                print("\nPressure Far-Field boundary condition requires the energy-equation to be activated (density formulation must be \'ideal-gas\' or \'real-gas\').")
                sys.exit()
            elif self._energy == True:  # compressible case
                pass
            else:
                print("\nInvalid energy formulation")
                sys.exit()
        def pressureInlet(self, name, totalPressure=0, staticPressure=0, components=[0,0,0], turbulenceIntensity=5, turbulentViscosityRatio=10, totalTemperature=300):
            pass

        def wall(self, name, slip='no', temperature=300, surfaceRoughness=[0.5, 1e-5]):
            pass

        def pressureOutlet(self, name, gaugePressure=0, staticTemperature=300):
            pass
        def outflow(self, name):
            pass

        def interface(self, name):
            pass





    def cellZones(self, **kwargs):
        pass

    def interfacesStuff(self, **kwargs):
        pass


    def methods(self, scheme='coupled', formulation='implicit', fluxType='roe-fds', skewnessCorrection=0, neighborCorrection=1, volumeFraction='geo-reconstruct', gradient='least-squares-cell-based', pressure='second-order', momentum='second-order-upwind', 'energy'='second-order-upwind',
                density='second-order-upwind', turbulentKineticEnergy='second-order-upwind', turbulentDissipationRate='second-order-upwind', pseudoTransient='yes',
                warpedFaceGradientCorrection='no', higherOrderTermRelaxation='no', transientFormulation='bounded-second-order-implicit'):
        pass

    def controls(self, courantNumber=200, pressure=0.3, density=1, bodyForces=1, momentum=0.7, turbulentKineticEnergy=0.8, turbulentSpecificDissipation=0.8):
        pass

    def writeCase(self, case, binary=True):
        """
        Write Fluent case file in the format of ".cas" or ".cas.h5" (ascii or binary)

        ----------
        Parameters
        ----------

        #1 case     :   case name or -path to the ".msh" file. If no path is given, the "workingDir" in the "runFluentCase"
                        function will be assumed as the path to the file. It is recommended to always provide the absolute path or specify
                        the working dir when setting up a Fluent simulation (workingDir)

        #2 binary   :   If True, write binary Files
        """


        if binary == False:
            tempString = "\n/file/write-case {}".format(case)
        else:
            tempString = "\n/file/write-case {}".format(case)


        self._writeCase = tempString



def generateCase(simulation):
    """
    Generates a Ansys Fluent input string based on the provided simulation argument.

    ----------
    Parameters
    ----------

    #1 simulation   :   Name of your simulation (python object variable). In Ansys Fluent, one would say a "case".
                        For instance, one would name a case "backwardFacingStep" and assign the object variable name
                        to it as "backwardFacingStep = Simulation()"
    """
    # Loop over own class attributes and filter out methods and empty attributes
    attr = [a for a in dir(simulation) if not a.startswith('__') and not callable(getattr(simulation, a)) and getattr(simulation, a) != None]
    fluentString = ""  # Initialize Fluent input string
    for command in attr:
        fluentString += "\n" + getattr(simulation, command)
    setattr(simulation, "_fluentString", fluentString)


def exportCase(simulation, caseName, path=os.getcwd()):
    """
    Exports your simulation to an Ansys Fluent input file (".jou"), based on the given caseName and path

    ----------
    Parameters
    ----------

    #1 simulation   :   Name of your python object variable. In Ansys Fluent, one would say a "case".
                        For instance, one would name a case "backwardFacingStep" and assign the object
                        variable name to it as "backwardFacingStep = Simulation()"

    #2 caseName     :   Name of your Fluent Input file / case name. The file extension (".jou") is automatically generated if not given.

    #3 path (opt.)  :   Directory, where the input file shall be exported to.
    """
    # If provided path argument doesn't end with "/", append slash to it for proper Linux file path
    if not path.endswith("/"):
        path += "/"

    # If provided caseName argument doesn't end with ".jou", append Ansys Fluent input file extension
    if not caseName.endswith(".jou"):
        caseName += ".jou"

    if not os.path.exists(path):
        print("Provided path in \'exportFluentCase(simulation, caseName, path)\'doesn't exist, please provide valid directory")
        sys.exit()

    with open(path + caseName, "w") as f:
        f.write(getattr(simulation, "_fluentString"))
        f.close()

    print("\nFluent input file has successfully been generated.")


def runCase(inputFile, simulation=None, GUI=False, plotResiduals=True, workingDir=os.getcwd()):
    """
    Exports your simulation to an Ansys Fluent input file (".jou"), based on the given caseName and path

    ----------
    Parameters
    ----------

    #1 inputFile     :   Name or path of the Fluent input file (".jou"); if no path is provided, the Python script folder is assumed
                         to be the folder containing the inputFile.

    #2 workingDir    :   Directory, where Fluent will be run.

    #3 GUI           :   If "True", Fluent will be launched in GUI mode with the inputFile automatically being run after the GUI is loaded.

    #4 plotResiduals :   If "True", the residuals ("continuity", "x-momentum", "y-momentum", etc.) will be plotted in a new window,
                         additionally to the printed residuals in the terminal. Can only be "True" if 'GUI = False'.
    """

# # Initialize simulation
sim1 = Simulation('2d-axisymmetric')

# # Setup simulation
# sim1.readMesh("RAE2822.msh")
# sim1.time("transient")
# sim1.solver("pressure-based", "coupled")
# sim1.turbulenceModel("k-epsilon",
#                      "realizable",
#                      "enhanced",
#                      "compressibility-effects")

# # Export and run simulation
# generateFluentCase(sim1)
# runCase(sim1, gui=False, plotResiduals=True)


sim1.boundaryCondition.velocityInlet(name='pipeInlet', components: [10, 0, 0], staticPressure: 1e4, turbulenceIntensity: 5, turbulentViscosityRatio: 10, staticTemperature: 298)
sim1.boundaryCondition.wall(name='duct', slip='no', temperature=300, surfaceRoughness=[0.5, 1e-5])
sim1.boundaryConditions.pressureOutlet(name='pipeOutlet', gaugePressure=0, staticTemperature=300)
