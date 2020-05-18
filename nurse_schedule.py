from __future__ import print_function
from ortools.sat.python import cp_model
import sys
from ortools.constraint_solver import pywrapcp



def main():
    # This program tries to find an optimal assignment of nurses to shifts
    # (3 shifts per day, for 7 days), subject to some constraints (see below).
    # Each nurse can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    num_nurses = 5
    num_shifts = 3
    num_days = 7
    num_skills = 2
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    all_skills = range(num_skills)

    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d,
                        s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))

    # H1: A nurse can be assigned to at most one shift per day.
    for n in all_nurses:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 1)

    # H2: The number of nurses for each shift for each skill equal to the minimum requirement.
    # H4: A shift of a given skill must necessarily be fulfilled by a nurse having that skill.
    # Each shift is assigned to exactly one nurse in .
    # Required shift per day: [Early, Late, Night] for each day
    # Different skills of nurses: (HeadNurse, Nurse)
    shift_require = [[[1,1],[1,1],[0,0]], # Monday
                     [[0,1],[0,1],[1,1]], # Tuesday
                     [[0,1],[1,0],[0,1]], # Wednesday
                     [[0,0],[0,0],[0,1]], # Thursday
                     [[0,1],[0,1],[1,1]], # Friday
                     [[1,1],[0,1],[1,0]], # Saturday
                     [[0,0],[0,1],[0,1]]] # Sunday
    for d in all_days:
        for s in all_shifts:
            for h in all_skills:
                if shift_require == 1:
                    if h == 1:
                        model.Add(shifts[(n, d, s)] for n in all_nurses == 1)
                    else:
                        model.Add(shifts[(n, d, s)] for n in range(3) == 1)
    # for d, s, h in shift_require:
        # model.Add(shifts[(n, d, s)] for n in all_nurses == 1)

    # H3: The shift type assignments of one nurse in two consecutive days must belong to the legal successions provided.
    # Penalized transitions: (previous_shift, next_shift)
    penalized_transitions = [
    # Late to Early is forbidden.
    (1, 0),
    # Night to Early and Late is forbidden.
    (2, 0),
    (2, 1)]

    for previous_shift, next_shift in penalized_transitions:
        for n in all_nurses:
            for d in range(num_days-1):
                transition = [
                    shifts[n, previous_shift, d].Not(),
                    shifts[n, next_shift, d + 1].Not()
                ]
                model.AddBoolOr(transition)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)
    for d in all_days:
        print('Day', d)
        for n in all_nurses:
            for s in all_shifts:
                if solver.Value(shifts[(n, d, s)]) == 1:
                     print('Nurse', n, 'works shift', s)
        print()


if __name__ == '__main__':
    main()