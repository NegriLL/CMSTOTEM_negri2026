#!/usr/bin/env python3

import ROOT
import sys

from pathlib import Path

# This is really annoying to write but python doesn't support some operations neatly
ROOT.gInterpreter.Declare("""
using namespace ROOT::VecOps;

bool HasTwoPairs(const RVec<float>& q) {
    if (q.size() != 4) return false;
    int pos = 0, neg = 0;
    for (auto v : q) {
        if (v > 0) pos++;
        else if (v < 0) neg++;
    }
    return pos == 2 && neg == 2;
}
 
std::vector<std::vector<double>> ComputePairMasses(const RVec<float>& q,
                                                    const RVec<float>& pt,
                                                    const RVec<float>& eta,
                                                    const RVec<float>& phi) {
    const double mass_hyp = 0.13957;
 
    std::vector<int> pos_idx, neg_idx;
    for (size_t i = 0; i < q.size(); ++i) {
        if (q[i] > 0) pos_idx.push_back(i);
        else if (q[i] < 0) neg_idx.push_back(i);
    }
 
    auto makeLV = [&](int i) {
        return ROOT::Math::PtEtaPhiMVector(pt[i], eta[i], phi[i], mass_hyp);
    };
 
    auto p1 = makeLV(pos_idx[0]);
    auto p2 = makeLV(pos_idx[1]);
    auto n1 = makeLV(neg_idx[0]);
    auto n2 = makeLV(neg_idx[1]);
 
    // (pi+1,pi-1) + (pi+2,pi-2) and (pi+1,pi-2) + (pi+2,pi-1)
    double massA1 = (p1 + n1).M();
    double massA2 = (p2 + n2).M();
    double massB1 = (p1 + n2).M();
    double massB2 = (p2 + n1).M();

    return {{massA1, massA2}, {massB1, massB2}};
}
""")




def filter_kinematics(file, save_path, pion_mass = 0.13957):
    df = ROOT.RDataFrame("tree", str(file))

    # Charge Sum
    charge = "trk_q[0] + trk_q[1] + trk_q[2] + trk_q[3]"

    # proton track cuts
    trk_px_sum = "trk_pt[0] * cos(trk_phi[0]) +" \
                 "trk_pt[1] * cos(trk_phi[1]) +" \
                 "trk_pt[2] * cos(trk_phi[2]) +" \
                 "trk_pt[3] * cos(trk_phi[3])"
    trk_py_sum = "trk_pt[0] * sin(trk_phi[0]) +" \
                 "trk_pt[1] * sin(trk_phi[1]) +" \
                 "trk_pt[2] * sin(trk_phi[2]) +" \
                 "trk_pt[3] * sin(trk_phi[3])"
    px_sum = "pr_px_a + pr_px_b"
    py_sum = "pr_py_a + pr_py_b"


    # Defining new kinetic branches
    df = (df.Filter(f"{charge} == 0")                                                   # Only events with no net charge
            .Filter("HasTwoPairs(trk_q)")                                               # Only events with two positive and two negative pions
            .Define("px_diff", f"fabs({trk_px_sum} + {px_sum})")                        # proton-track momentum difference px
            .Define("py_diff", f"fabs({trk_py_sum} + {py_sum})")                        # proton-track momentum difference py
            .Define("pair_masses", "ComputePairMasses(trk_q,trk_pt, trk_eta, trk_phi)") # both permutations of rhos
    )


    df.Snapshot("tree", str(save_path))


def main():
    if len(sys.argv) != 3:
        print("Error: Incorrect number of arguments. Need 2 files.")
        sys.exit(1)

    file = Path(sys.argv[1])
    save_path = Path(sys.argv[2])
    save_path.parent.mkdir(parents=True, exist_ok=True)

    filter_kinematics(file, save_path)


if __name__ == "__main__":
    main()