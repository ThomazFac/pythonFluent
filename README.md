# pythonFluent
Interface for [**Ansys Fluent**][ansys-fluent] to drastically reduce time for setting up your CFD simulations using Python scripts. Moreover, a new input script file type is introduced to further simplify and improve in particular preprocessing and simulation setup tasks.

[ansys-fluent]: https://www.ansys.com/products/fluids/ansys-fluent
    
## Install
The recommended way is to use ```pip```:
```sh
# With pip
pip install pythonfluent
```
You can also clone the repository to your PC and then install it with Python 3:
```sh
# With git
git clone https://github.com/rap7or/pythonFluent
cd pythonfluent/
python3 install.py
```

## Quickstart
The recommended way to learn ```pythonFluent``` is to go through the tutorials in the ```tutorials/``` folder and 
to check out the examples in the ```examples/``` folder. Furthermore, a read-the-docs page with the complete documentation of the 
project can be found [**here**][read-the-docs]. 

[read-the-docs]: https://read-the-docs.io

A quick example of how a `pythonFluent` input script is created including running and saving an Ansys Fluent simulation, consider a transonic airfoil case at ```Ma = 0.8```:

``` python
#/usr/bin/python
# file: NACA0012.py
import pythonFluent

# Initialize the simulation 
case1 = pythonFluent.Simulation('2d-planar')

# Import mesh and set the solver
case1.readMesh('NACA0012.msh')
case1.solver('pressure-based', 'coupled')

# Set the turbulence model, set the energy equation and material properties
case1.turbulenceModel('spalart-allmaras', 'strain-vorticity-based')
case1.energy('yes')
case1.material('air', density='ideal-gas', viscosity='sutherland')
case1.cellZone(name='domain', 'fluid', material='air')

# Define boundary conditions
case1.boundaryCondition.pressureFarfield('farfield', components=[0.8, 0], 
                                          staticPressure=3e4, temperature=240)
case1.boundaryCondition.wall('airfoil', slip='no', temperature=240)

# Set the discretization
case1.methods(pressure='second-order-upwind', momentum='second-order-upwind', 
              nu='second-order-upwind')

# Initialize and run
case1.initialize('hybrid-initialization', 10)
runCase(case1, iterations=200, GUI=False, plotResiduals=True)

# Export .cgns files and save case
case1.exportData('NACA0012_transonic.cgns', 'axial-velocity', 'radial-velocity',
                 'static-pressure', 'density')
case1.saveCase('NACA0012')
case1.saveData('NACA0012')
```
Just run the script using ```python3 NACA0012.py```.

## New input script file type
The problem with using the Fluent commands (which are written in SCHEME) is that a small typo or wrongly 
set bracket will make execution unsuccessful. Sometimes, changing settings of your simulation results in minutes spent on finding the correct command. Therefore, a new input script type has been developed based on 
the `pythonFluent` module to drastically improve the setup of a new simulation as user-friendly as possible. Another advantage is
that this approach allows massive parametrization of your models for design and optimization by combining the `pythonFluent` module
with the new input script type.

Consider the Python script shown in the [previous headline](## Quickstart). With the new input script type, the translated Python script would look like this:

``` sh
# file: NACA0012.in

dimension           2d-planar
read-mesh           NACA0012.msh
time                steady-state
solver              pressure-based, coupled, pseudo-transient
turbulence-model    spalart-allmaras, strain-vorticity-based
energy              yes
material            air, ideal-gas, viscosity=sutherland
cell-zone           domain, fluid, air
pressure-far-field  far-field, [0.8, 0], staticPressure=3e4, temperature=240
wall                airfoil, no-slip, temperature=240
methods             pressure=second-order, momentum=second-order-upwind, 
                    nu=second-order-upwind
initialize          hybrid-initialization, 10
calculate           iterations=200, gui=false, plot-residuals=true
export-data         cgns, NACA0012_transonic, axial-velocity, radial-velocity, 
                    static-pressure, density
save-case-data      NACA0012
```
All done in 16 lines! You can run the input file by importing it with the pythonFluent module
and executing the Python script. However, it is recommended to directly run the script using the command
`pythonfluent NACA0012.in`.

