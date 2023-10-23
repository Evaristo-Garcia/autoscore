# Evaristo Garcia Reyna - Michigan Baja Racing
# 6/10/2022

# Used in Part 1 JSON creation
class Teams:
    def __init__(self, num):
        self.num = num
        self.school = 'School'
        self.name = 'Default'
        self.sales = 0.0
        self.cost = 0.0
        self.design = 0.0
        self.accel = 0.0
        self.maneuv = 0.0
        self.sled = 0.0
        self.sus = 0.0
        self.static = 0.0
        self.dynamic = 0.0
        self.overall = 0.0

    def sum_static(self):
        self.static = sum([self.sales, self.cost, self.design])

    def sum_dynamic(self):
        self.dynamic = sum([self.accel, self.maneuv, self.sled, self.sus])

    def sum_overall(self):
        self.sum_static()
        self.sum_dynamic()
        self.overall = self.static + self.dynamic


class EnduranceTeam:
    def __init__(self, num: str, school: str, name: str, current_lap: int, final_lap: int, overall_score: float):
        self.num = num
        self.school = school
        self.name = name
        self.current_lap = current_lap
        self.final_lap = final_lap
        self.endurance_score = 0.0
        self.overall_score = overall_score
        self.bonus = 0.0
        self.predicted_overall_score = 0.0

    def sum_endurance_overall(self):
        self.predicted_overall_score = self.overall_score + self.endurance_score + self.bonus
