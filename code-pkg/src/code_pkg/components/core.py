from cheartpy.fe.api import (
    create_basis,
    create_boundary_basis,
    create_top_interface,
    create_topology,
    create_variable,
)

from code_pkg.types import FluidVariables, ProblemTopology, SolidVariables, TopDef

_INT2STR = {0: "const", 1: "lin", 2: "quad"}


def create_problem_topology(mesh: TopDef) -> ProblemTopology:
    solidbasis = {
        i: create_basis(mesh["solid"][i]["elem"], "NL", i, quadrature="GL", gp=6) for i in [1, 2]
    }
    fluidbasis = {
        i: create_basis(mesh["fluid"][i]["elem"], "NL", i, quadrature="GL", gp=6) for i in [0, 1, 2]
    }
    bndbasis = create_boundary_basis(solidbasis[2])
    solidtops = {
        i: create_topology(
            f"TPSolid{_INT2STR[i]}",
            basis=solidbasis[i],
            mesh=mesh["home"] / mesh["solid"][i]["name"],
        )
        for i in [1, 2]
    }
    fluidtops = {
        i: create_topology(
            f"TPFluid{_INT2STR[i]}",
            basis=fluidbasis[i],
            mesh=mesh["home"] / mesh["fluid"][i]["name"],
        )
        for i in [0, 1, 2]
    }
    fluidtops[0].discontinuous = True
    bndtop = create_topology("TPBnd", basis=bndbasis, mesh=mesh["home"] / "bnd")
    bndtop.create_in_boundary(solidtops[1], mesh["solid_bcpatch"]["interface"])
    solidbody = create_top_interface("OneToOne", [*solidtops.values()])
    fluidbody = create_top_interface("OneToOne", [*fluidtops.values()])
    fluid_interface = create_top_interface(
        "ManyToOne",
        [bndtop],
        master=fluidtops[2],
        interface_file=mesh["home"] / "iface-fluid.IN",
        nest_in_bnd=mesh["fluid_bcpatch"]["interface"],
    )
    solid_interface = create_top_interface(
        "ManyToOne",
        [bndtop],
        master=solidtops[2],
        interface_file=mesh["home"] / "iface-solid.IN",
        nest_in_bnd=mesh["solid_bcpatch"]["interface"],
    )
    return ProblemTopology(
        {hash(h): h for h in [solid_interface, fluid_interface, solidbody, fluidbody]},
        fluid2=fluidtops[2],
        fluid1=fluidtops[1],
        fluid0=fluidtops[0],
        solid2=solidtops[2],
        solid1=solidtops[1],
        bnd=bndtop,
    )


def create_fluid_variables(top: ProblemTopology) -> FluidVariables:
    prefix = "Fluid"
    xt = create_variable(f"{prefix}Xt", top.fluid1, 2, data=top.fluid1.mesh)
    x0 = create_variable(f"{prefix}X0", top.fluid1, 2, data=top.fluid1.mesh)
    return FluidVariables(
        Xt=xt,
        X0=x0,
        V=create_variable(f"{prefix}V", top.fluid2, 2),
        P=create_variable(f"{prefix}P", top.fluid1, 1),
        W=create_variable(f"{prefix}W", top.fluid1, 2),
    )


def create_solid_variables(top: ProblemTopology) -> SolidVariables:
    prefix = "Solid"
    x = create_variable(f"{prefix}X", top.solid2, 2, data=top.solid2.mesh)
    return SolidVariables(
        X=x,
        V=create_variable(f"{prefix}V", top.solid2, 2),
        U=create_variable(f"{prefix}U", top.solid2, 2),
        P=create_variable(f"{prefix}P", top.solid1, 1),
    )
