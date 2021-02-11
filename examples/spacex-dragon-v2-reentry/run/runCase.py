import pythonFluent

# General settings
dragon_v2 = pythonFluent.Simulation("3d")
dragon_v2.readMesh('dragon_v2.msh')
dragon_v2.time('steady-state')
dragon_v2.solver('density-based', 'implicit', 'roe-fds')

# Fluid-dynamic settings
dragon_v2.turbulenceModel('inviscid')
dragon_v2.energy('yes')
dragon_v2.cellZones('domain', 'fluid')

# Boundary conditions
dragon_v2.boundaryCondition.pressureFarField('farfield', components=[10, 0, 0], temperature=170,
                                              turbulenceIntensity=0.05, turbulentViscosityRatio=5)
dragon_v2.wall('vehicle')
dragon_v2.cellZones('domain', 'fluid')

# Numerical settings
dragon_v2.methods(pressure='second-order', momentum='second-order-implicit')

# Solution
dragon_v2.initialize('hybrid-initializatio', 10)
dragon_v2.calculate(iterations=300, plotResiduals='yes', gui='no')
dragon_v2.exportData('results/dragon_v2', 'cgns', 'x-velocity', 'y-velocity', 'z-velocity', 'pressure', 'density', 'temperature')
dragon_v2.saveCaseData('results/dragon_v2_reentry')
