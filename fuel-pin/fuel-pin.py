
import openmc
import openmc_data_downloader
import os.path
import urllib.request


def create_geometry():
    _DAGMC_FILE = "dagmc.h5m"
    if not os.path.exists(_DAGMC_FILE):
        u = urllib.request.urlopen('https://tinyurl.com/y3ugwz6w')
        assert u.status == 200, 'Failed to download file.'
        with open(_DAGMC_FILE, 'wb') as f:
            f.write(u.read())
    openmc.Geometry(root=openmc.DAGMCUniverse(filename=_DAGMC_FILE)).export_to_xml()


def create_materials():
    # fuel found by name
    u235 = openmc.Material(name="fuel")
    u235.add_nuclide('U235', 1.0, 'ao')
    u235.set_density('g/cc', 11)
    # water found by id
    water = openmc.Material()
    water.add_nuclide('H1', 2.0, 'ao')
    water.add_nuclide('O16', 1.0, 'ao')
    water.set_density('g/cc', 1.0)
    water.add_s_alpha_beta('c_H_in_H2O')
    water.id = 41
    materials = openmc.Materials([u235, water])
    materials.export_to_xml()
    openmc_data_downloader.just_in_time_library_generator(
        libraries='ENDFB-7.1-NNDC',
        materials=materials
    )


def create_settings():
    settings = openmc.Settings()
    settings.batches = 10
    settings.inactive = 2
    settings.particles = 5000
    settings.export_to_xml()
    settings.source = openmc.Source(
        space=openmc.stats.Box(
            [-4., -4., -4.],
            [ 4.,  4.,  4.],
        ),
    )
    settings.export_to_xml()


def create_tallies():
    # tally = openmc.Tally()
    # tally.scores = ['total']
    # tally.filters = [openmc.CellFilter(1)]
    # openmc.Tallies([tally]).export_to_xml()

    cell_tally = openmc.Tally(name='heating')
    cell_tally.scores = ['heating']

    mesh = openmc.RegularMesh()
    mesh.dimension = [50, 50, 50]
    mesh.lower_left = [-12, -12, -2]  # x,y,z coordinates start at 0 as this is a sector model
    mesh.upper_right = [12, 12, 2]

    mesh_tally = openmc.Tally(name="heating_on_mesh")
    mesh_tally.filters = [openmc.MeshFilter(mesh)]
    mesh_tally.scores = ["heating"]

    openmc.Tallies([cell_tally, mesh_tally]).export_to_xml()


create_geometry()
create_materials()
create_settings()
create_tallies()
openmc.run()
