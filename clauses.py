def calc_design_wind(Vb, k1=1.0, k2=1.0, k3=1.0, k4=1.0):
    Vz = Vb * k1 * k2 * k3 * k4
    Pz = 0.6 * Vz * Vz

    return {
        "Vb": {
            "value": Vb,
            "unit": "m/s",
            "ref": "IS 875 (Part 3):2015, Cl. 5.2"
        },
        "Vz": {
            "value": round(Vz, 2),
            "unit": "m/s",
            "ref": "IS 875 (Part 3):2015, Cl. 6.3"
        },
        "Pz": {
            "value": round(Pz, 1),
            "unit": "N/m²",
            "ref": "IS 875 (Part 3):2015, Cl. 7.2.1"
        }
    }